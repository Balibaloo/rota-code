# Frame 190, pass 2, the route, the reply and the slice: where things are

Status: written by the implementer of pass 2 on 2026-10-09, after the
gate. Rota workflow, except where a line says meta workflow. The design is
`plans/frame190-design.md`. Pass 1 and 1b are in
`plans/frame190-pass1.md`.

## What landed, by design point

- **2.2.1 and 2.F.2, a team's note takes no revise.** `rota/roles/api.py`,
  `rulings_rule`, with the new helper `_is_team_note`. A `revise` on a
  ledger row, a constraint, a glossary term or a model area is refused
  when the page numbers a request item. The refusal names every request
  line: "line 9 is the team's note, not your request. revise rewrites a
  line of what the principal asked for: line 1, <item a>, or line 5,
  <item b>. Revise the line the words are about. To drop the note, contest
  it."
- **2.2.2, a revise carries the words.** `rota/core/runner.py`,
  `_resolve_contest`. The function reads `contest` or `revise`, and
  `principal_verdict` carries the ruling the principal gave.
- **2.2.3.** Landed in pass 1b through the `stamped:` row. Not built again.
- **2.2.4, the relay cannot undo a ruling.** `rota/roles/api.py`,
  `problem_set_approval`, with the new helper `_principal_relay`. In a
  session woken by a relay of a principal verdict, a state other than the
  one `land` wrote for the item is refused: "the principal ruled <item>
  revise. land wrote `contested`, and the contested wake carries the
  words. Leave it".
- **2.2, the batch line, points 1 to 7.**
  - `rulings_rule` admits a contest or a revise of a batch line when the
    batch has no head commit. After the head commit, frame 142's refusal
    stands, with the item's line named.
  - `rota/roles/principal.py`, `land`, keeps a contested or revised batch
    ref in the verdict when the batch has no head commit. An approve of a
    batch line is still dropped.
  - `rota/core/sandbox.py`, `_owner_of_ref`, gives a batch to `architect`.
    The relay split keys a batch apart with `BATCH_RELAY`, as
    `CRITERIA_RELAY` keys the criteria.
  - `rota/core/scheduler.py`, `batch_relay`, and `rota/core/runner.py`,
    `_mode_key`: an Architect relay of batches alone, caused by a verdict,
    keys `annotate`.
  - `rota/roles/api.py`, `batches_annotate`: in a session woken by a relay
    of a verdict that contests or revises the batch, the first call stages
    one clear write before its rows, so the new prediction replaces the
    old. `rota/core/runner.py`, `_as_write`, and `rota/core/db.py`,
    `_apply_write`, carry the new write op `clear` for a junction table.
  - `rota/core/runner.py`, `resolve_inbound`: a relay of batches carries
    `touch`, the `touch_set` of each batch, so the Architect sees the
    prediction it corrects.
  - `architect/annotate.md` gains the paragraph of the design, word for
    word. `liaison/verdict_signoff.md` gains "a batch —
    `msg.relay_architect`" and `batches` in the owner sentence. The
    criterion line already read `msg.relay_terminologist`.
- **2.3.1, no row about the ruled row.** `rota/roles/api.py`, `ledger_log`:
  in a session woken by a relay of a principal verdict, an `about_ref`
  that is a ref of that relay is refused with the design's sentence.
- **2.3.2, the four-word floor.** `ledger_log` refuses an assumption of
  fewer than four words with the design's sentence.
- **2.F.7, a message is no row.** `ledger_log` refuses an `about_ref` that
  is a row of `messages`, first among its doors.
- **2.3.3, one id.** `model_adopt` and `glossary_adopt` read a string
  `ids` as a list of one id.
- **2.3.4, the brief.** `architect/relay.md` holds the design's paragraph
  in place of "If the contest tells you an assumption you made,
  `ledger.log` it."
- **2.7 and 2.F.4, the slice again.**
  - `rota/core/schema.sql`, `tickets.item_ver`, and the migration in
    `rota/core/db.py`, `init_db`, which adds the column to an older
    database. NULL is unknown.
  - `rota/roles/api.py`, `tickets_slice`, writes `item_ver` from
    `items.version`.
  - `rota/core/scheduler.py`, `tick_slicing`, also wakes for an approved
    in-scope item whose version is above the newest `item_ver` of its
    tickets, when no ticket of the item sits in a live batch. A live batch
    blocks the wake, so the cancel of the ruling of 2026-09-12 goes first.
  - `rota/core/scheduler.py`, `not_retired`: a ticket below the newest
    `item_ver` of its item is retired. `tick_criteria`, and
    `rota/core/predicates.py`, `grouping` and `tests_missing`, read live
    tickets only.
- **Question 5.2, the Tester's paths.** `rota/core/runner.py`,
  `push_working_set`: a `tick:tests_missing` wake pushes `touch`, the
  batch's expected paths under `tests/`. `tester/tests_missing.md` says "A
  path under `touch` is the file the principal expects your tests in. Use
  it." in place of "Nobody assigns them."

## Review fixes of 2c602d1b

1. High. `land` no longer contests a note's `about_ref` when that row is
   a request row the door stamped. A note about c1 no longer turns the
   approve of c1 into a contest.
2. Low. `_bind_send.stage` records `stalled:` on every present to the
   principal, from any wake: the quarantined keys of the page's batches
   at the send.
3. Low. `request_block` and `_gave_up_tries` read the page's `stalled:`
   keys, never the live quarantine. The m84 test asserts three
   `check: none yet.` lines and no "gave up".
4. Low. The stamp is every request row that the wake did not name: not in
   `ctx.wake_refs` and not in the trigger message's refs. A row the model
   named is stamped.
5. Low. `_bind_send.stage` refuses `msg.answer_tester` from a
   `criterion_repair` relay when no live batch of the criterion has a
   head commit. `terminologist/criterion_repair.md` says "on a page" and
   sends `answer_tester` only when the change has a commit.
6. Low. The split stages its key on each relay as `split`, and
   `stage_park_relay` finds the criteria relay by the key
   `terminologist:criteria`. The key never reaches a message.
7. Low. `_is_request_item` needs the item's version above its
   `delivered:` row, the rule of `open_requests`.
8. Held, no change.

## Deviations from the design

- The relay split keys a batch apart, `BATCH_RELAY`, and `_mode_key` keys
  `annotate` only for a relay of batches alone (reasoned: a relay that
  holds a batch and a constraint would lose `model.adopt` in `annotate`;
  this is the shape of the criteria relay of pass 1b).
- The replacement of the touch set is a pipeline write op, `clear`, and
  not a `withdrawn` confidence (reasoned: `batch_touch.confidence` has a
  CHECK of two values, so `withdrawn` needs a table rebuild; the pipeline
  had no delete, and the op is limited to junction tables).
- An Architect relay of batches carries `touch`, the current prediction
  (reasoned: the brief says to keep every path the words do not dispute,
  and a relay wake showed no prediction; only a relay of batches pushes the
  key, so no recorded prompt moves).
- `_resolve_contest` carries the ruling the principal gave, `revise` or
  `contest`, in `principal_verdict` (reasoned: the design names no value,
  and the true word is the one the record holds).
- Review fix 1 is narrower than the review's line: a note's contest skips
  the `about_ref` only when that row is a stamped request row (reasoned:
  the wide form, any line of the page, broke
  `test_contesting_an_assumption_overrules_it_and_contests_its_row` and
  `test_the_liaison_records_the_ruling_by_line_and_the_door_lands_it`,
  which pin the rule of 2026-09-12 that a note's contest contests a wake's
  own row; the review's case E is a stamped criterion, and it holds).
- `tests_encode` checks that the criterion exists before it offers a
  triage call (reasoned: the follow check needs an offer that lands, and a
  new recording sent three ids joined by commas; outside the design, and
  needed to keep `ACT-TS-three-criteria-one-per-reply` green).
- The re-annotate case seeds four `code_index` rows from night 136
  (reasoned: without an index the seat cannot know that
  `tests/test_termui.py` exists; the case stays red with them).
- The tests that asserted the old words were rewritten to their intent:
  `test_touch_note.py`, a contest of the batch line before the build stays
  in the verdict and leaves it after the head commit;
  `test_laws.py` and `test_identity.py`, the assumptions grew to four
  words; `test_park_page.py`, the hand-built criteria relay carries the
  split key the door stages.

## Tests

`tests/rota/test_request_page.py` holds 21 tests, 10 of them new in this
pass:

- a revise of the item line lands with m400's words, and a revise of the
  note is refused with lines 1 and 5 named;
- the Vision Keeper's relay of m76 cannot set the revised item approved;
- a contest of bg_2's prediction on m85 reaches the Architect's
  `annotate`, the touch set is replaced, and the Tester's wake shows
  `tests/test_termui.py`;
- after the head commit the batch line is refused with the item named;
- s559's `ledger.log` is refused, `model.adopt(ids=<one id>)` skips the
  id, and a message as `about_ref` is refused;
- s87's one-word assumption is refused;
- night 133's `confirm_default_on_eof` at version 8 is sliced again, the
  old ticket is retired, and `criteria` and `grouping` see the new ticket
  alone;
- review fixes 1, 2 with 4, 5 and 7, one test each. Fix 3 is in the m84
  test, and fix 6 in the park page test.

Two new recorded cases in `tests/rota/cases/l1_architect.yaml`:
`L1-AR-a-ruled-constraint-gets-no-new-row` and
`L1-AR-re-annotate-from-the-principals-correction`, 5 runs each.

## The gate, verbatim

The gate ran three times. The first run found the main card held and
re-recorded nothing. The second re-recorded 18 cases. The third re-earned
`ACT-TS-three-criteria-one-per-reply` after the `tests_encode` change. Its
five lines:

```
suite: 26 failed, 3449 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (5): tests/rota/test_l1.py::test_l1_case[L1-AR-re-annotate-from-the-principals-correction], tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l1.py::test_l1_case[L1-TS-an-outside-fact-is-the-researchers]
stale (0): none
time: 604.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

Four new reds are the four known before this pass. The fifth is this
pass's new case `L1-AR-re-annotate-from-the-principals-correction`, red
0 of 5. `L1-TS-an-outside-fact-is-the-researchers` is a new red gone.

## Re-records

The gate's second run, qwen3:8b, a refresh run and a plain run each:

- green 5/5: `ACT-TS-five-criteria-one-per-reply`,
  `ACT-TS-give-the-prompt-a-stream`, `L1-AR-a-ruled-constraint-gets-no-new-row`
  (new), `L1-AR-adopt-what-the-principal-approved`,
  `L1-LI-a-park-verdict-sends-its-contested-criterion-to-the-terminologist`,
  `L1-LI-a-ruling-splits-by-owner`, `L1-LI-relay-a-ruling-without-interpreting-it`,
  `L1-TE-adopt-what-the-principal-approved`,
  `L1-TE-repair-the-criterion-the-tester-cannot-encode`,
  `L1-TS-a-criterion-that-contradicts-the-request-goes-back`,
  `L1-TS-encode-a-criterion`.
- green 4/5: `L1-AR-annotate-a-batch`,
  `L1-TS-a-criterion-no-machine-could-check-is-vision_keepers`.
- provisional: `L1-LI-say-what-the-run-could-not-see` 1/1,
  `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` 5/5,
  `L1-TS-an-outside-fact-is-the-researchers` 5/5.
- `ACT-TS-three-criteria-one-per-reply`: green 5/5, then red on the
  follow check. The seat sent three criterion ids joined by commas, and
  the triage offer of `tests_encode` named that id. `tests_encode` now
  checks the criterion before the offer. The third gate re-earned it green
  5/5.
- `L1-AR-re-annotate-from-the-principals-correction` (new): 0/5 on the
  gate's run, and 0/5 again on one hand re-record (`gate._rerecord`) after
  the case gained the index rows of night 136. Every run calls
  `batches.annotate`. The seat keeps the disputed `tests/test_defaults.py`
  in 3 of 5 runs without the index and in 5 of 5 with it, and it writes
  `tests/test_terminal.py` or `tests/test_terminal_ui.py` in place of
  `tests/test_termui.py`. It makes no `code.probe` call (observed: the
  re-record log, 2026-10-09).

## Unfinished

- `L1-AR-re-annotate-from-the-principals-correction` is red 0 of 5. The
  seat does not read the index for the path the words name, and it keeps
  the path the words dispute. A second shape of the `annotate.md`
  paragraph, or an interview of the seat, is the holding session's
  decision.
- Pass 3: change 2.4 with amendment 3.
- `tickets.scan` still lists a retired ticket to the Terminologist's
  criteria wake. The design names `tick_criteria`, `grouping` and
  `tests_missing` only.
- `_resolve_refs` resolves no batch, so a batch ref in a verdict carries
  no `table` for the Liaison. The door routes it by ownership.
