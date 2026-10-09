# Frame 190, pass 1, the page: where things are

Status: written by the implementer of pass 1 on 2026-10-09, after the
gate. Code commit `358fed11` on `rota/foundation`. Rota workflow, except
where a line says meta workflow. The design is `plans/frame190-design.md`.

## What landed, by design point

- **2.1.1 and 2.F.2, `request_rows`.** `rota/roles/principal.py`,
  `request_rows`, with `_items_reached`, `_is_request_item` and
  `open_requests`. The function returns each item that the refs reach, then
  the item's criteria in id order. With no item reached, it returns every
  open request, with no cap. With no open request, it returns the account.
  A description, an observed item and the account are never request items.
- **2.1.2, the door stamp.** `rota/core/sandbox.py`, `_bind_send.stage`,
  after the sign-off hook. Every present to the principal gets
  `request_rows` appended. The park message is left as it is.
- **2.1.3 and 2.F.5, `request_block`.** `rota/roles/principal.py`,
  `request_block`. The block renders the principal's quoted statements,
  each request item, and each item's criteria with their `check:` lines.
  `_park_page` calls it with `park=True`. `render_page` takes every block
  row out of the other groups, so `order` holds no duplicate id. The
  account stays under "What we are building:".
- **2.1.4, the team's notes.** `render_page`, the general present branch.
  The heading `TEAM_NOTES` stands above the assumptions, the terms and the
  other rows. The touch note's batch line stands under "The team expects
  to touch:".
- **2.1.5 and 2.F.2, the closing sentence.** `_name_request`: "To change
  what you asked for, name line 1." or "name its line, 1 or 5.".
- **2.5.1 and 2.5.2, the check lines.** `request_block` writes
  `check: none yet.`, or `check: none. The team gave up writing it after
  <n> tries.` when a quarantined `tests_missing` key names a batch that
  holds the criterion (`_gave_up_tries`).
- **2.5.3, a new file.** `touch_words(..., mark_new=True)`, called from
  `render_page` only. A predicted path under a `tests` folder that
  `code_index` lacks reads `(a new file)`.
- **2.5.4 and 2.F.6, the quarantined branch.** `render_page(...,
  stalled=None)`. The branch renders the block, then "The team gave up on:
  tests_missing for bg_2, 3 attempts.", then the prediction.
- **2.2.3 and 2.F.1, `land`.** `rota/roles/principal.py`, `land` and
  `_signoff_page`. Off the sign-off page and off the park page, an approve
  of a row that `request_rows(conn, ask.refs)` returns leaves `per_item`.
  A ruling with nothing left lands its verdict answered.
- **2.F.1, the relay filter.** `rota/core/scheduler.py`, `verdict_rows`,
  which `park_verdict_rows` now calls. `_bind_send.stage` drops a criterion
  from a relay when the verdict does not contest or revise it, on every
  page. A relay left with no ref is refused with a sentence that says so.

## Deviations from the design

- `stalled` is read from `tick_attempts` at render time, and no door writes
  a `stalled:<message id>` config row (reasoned: a session stages messages
  only, and a config row needs a write path in `db.py` or `runner.py`,
  outside the pass's files; the keys sit in `tick_attempts`, which the
  page reads at every render, and the order of the lines is the touch
  note's order, so a page that turns quarantined keeps its line numbers).
  The keyword argument exists, and a list overrides the read.
- `open_requests` orders by `priority DESC`, then id (reasoned: the design
  says "by priority" with no direction; `api.batches_list` and the cockpit
  order by `priority DESC`).
- The closing sentence lists the item lines joined by "or", not "<a> to
  <b>" (reasoned: criteria lines stand between two items, so a range
  names lines that are not requests).
- A second request item opens with "You also asked:" when the item before
  it had criteria (reasoned: the park page needs one "You asked:" heading
  word for word, and amendment 5 forbids a second "You asked:" heading).
- `rota/testkit/scenes.py`, `_Principal.respond`, reads the stamped tail
  off a page's refs before it looks up the scene's script (reasoned: the
  scene scripts key an answer by the exact refs the seat sent; without the
  read, 191 scene and invariant tests failed on the first gate).
- The gate ran twice with `--no-rerecord`, the re-records ran by hand, and
  the last gate ran plain (reasoned: the Bash call stops at ten minutes,
  and the plain gate re-records after the suite).

## Tests

- `tests/rota/test_request_page.py`, new, 8 tests: the agenda page of
  night 133's m122, the account of m118, the touch note of night 136's
  m84, the quarantined page of m96, every open request of m399, an "ok"
  off the sign-off page, the criterion relay filter, and the sign-off page
  that still approves.
- `tests/rota/test_park_page.py`, 1 new test: the park page of night 132's
  m117, word for word.
- Rewritten to the new page and kept to their intent:
  `test_principal_messaging.py` (1 test), `test_signoff_assumptions.py`
  (2 tests and the fixture), `test_principal_reply.py` (3 tests and the
  fixture), `test_chaos_confirm.py` (the fixture). The fixture presents
  that approve an item now have a `submit` cause.

## The gate, last run, verbatim

```
suite: 25 failed, 3427 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 605.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The four new reds are the four known before this pass.

## Re-records

Six `l1_landing.yaml` cases, each a refresh run and a plain run on
qwen3:8b at `ROTA_NUM_CTX=12288`, all green 5 of 5 on the replay:
`L1-LI-plain-agreement-approves-every-line`,
`L1-LI-a-named-line-is-contested-and-the-rest-approved`,
`L1-LI-a-correction-in-a-sentence-contests-the-line-it-is-about`,
`L1-LI-a-question-about-the-page-is-answered-not-ruled`,
`L1-LI-approve-one-line-only-approves-that-line-alone` and
`L1-LI-a-long-page-is-ruled-without-the-rows`. The seventh,
`L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`, renders
a confirm page that this pass does not change. Its replay is red on the
tree before this pass too (observed: replay at `135d07f2`, 2026-10-09).

## Unfinished

- Passes 2 and 3: 2.2 beyond 2.2.3, 2.3, 2.4 and 2.7.
- A non-park criterion still goes to `_owner_of_ref`, which knows no
  criterion. Change 2.2.7 in pass 2 sends it to the Terminologist.
  Pass 1b took this change, see below.

## Pass 1b

Code commit `2c602d1b`, the four findings of the diff review of
`358fed11`.

- **Finding 1, high: an account page approved the stamped requests.**
  `rota/core/sandbox.py`, `_bind_send.stage`, records the stamped rows in
  the config row `stamped:<message id>`. The row rides the staged message
  as `config`, and `db.session_commit` writes it with the message
  (`OutboundMessage.config`, `runner._messages_from`). `principal.land`
  drops an approve of a stamped row on every page, through `door_rows`.
  The sign-off test by cause, `_signoff_page`, is gone.
- **Finding 2, low: an item's own present no longer approved it.** Fixed
  by finding 1: the item is the wake's row, so its approve lands.
- **Finding 3, high: a contested criterion off the park page went
  nowhere.** Change 2.2.7 came into this pass. `scheduler.
  park_verdict_criteria` now returns the criteria a verdict contests or
  revises as lines of its page, on any page. `park_criterion_relay`
  accepts a relay of such criteria, so `_mode_key` gives
  `criterion_repair`. The relay split sends every criterion to the
  Terminologist. A criterion line goes in its own relay, keyed apart by
  `CRITERIA_RELAY`, and a term keeps its relay. `stage_park_relay` narrows
  only a relay that holds a criterion. `liaison/verdict_signoff.md` names
  the criterion's relay.
- **Finding 4, low: a live key turned an open touch note into a stopped
  page.** A send on `tick:quarantined` records its keys in
  `stalled:<message id>`. `render_page` reads that row and no longer
  reads `tick_attempts`.
- The docstring of the agenda "ok" test names m399, not m362.

Deviations, pass 1b:

- The record is a config row written in the session's commit (reasoned:
  a message column needs a schema migration, and a marker in the refs
  reaches every reader of `body_refs`; the config row is the shape that
  2.F amendment 6 names, and a refused session writes none).
- A criterion that reached the verdict through a contested ledger row's
  `about_ref` goes to the Terminologist in `relay`, not in
  `criterion_repair` (reasoned: it is no line of the page, so it is no
  ruling on its words, the diff review of b0a2086e, finding 1).
- `stage_park_relay` narrows a relay that mixes a term with a criterion
  to the contested criteria, and the term drops (reasoned: the park test
  of the diff review of 0baacf55 expects that narrowing; the split itself
  never mixes a term with a criterion line).

Tests, pass 1b: `tests/rota/test_request_page.py` now holds 10 tests. The
criterion test asserts the Terminologist and `criterion_repair`. The
sign-off test was replaced by night 133's m212 test. Two tests are new,
night 136's m128 and the re-rendered m84.

The gate, pass 1b, verbatim:

```
suite: 25 failed, 3429 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 649.8s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

Re-records, pass 1b: none. The gate read 0 stale cases after the change
to `verdict_signoff.md`, and the three `verdict_signoff` cases replay
green.
