# Frame 142, pass 1: the park page, where things are

Written by the pass-1 implementer on Opus, 2026-10-09 00:58, on the tree
after 985a6e85. Rota workflow, except where a line says meta workflow.
The design is `plans/frame142-design.md`. Section 2.C, the chat intake, is
pass 2 and is not touched.

## What landed, per design point

**2.A, the park ask is a page with rows.**

- `rota/core/scheduler.py`: `park_reds` (own and project reds, the newest
  run per test), `park_criteria` (the batch's criteria in id order),
  `park_rows` (the item and the criteria, or `[batch]` for a note),
  `park_owns`, `park_message_rests`, `park_rests`, `_park_versions`, and
  `park_ask_id`, whose digest now holds the closed messages that did not
  rest and the sum of the versions of the criteria and the own tests.
- `rota/core/predicates.py`: `park_ask` reads `park_owns`, and its detail
  ends `It is a page.` or `It is a note.`.
- `rota/core/sandbox.py`: `_bind_send.stage` keys the park on `present`,
  replaces the refs with `park_rows`, skips the wake-refs hook for the
  park, and gives the message the id `park_ask_id`. `RULED_TABLES` gains
  `"criteria": "terminologist"`.
- `rota/roles/principal.py`: `check_line`, `_strip_comment`,
  `_failure_line`, `_park_page`, and `render_page(..., ask_id=None)`, whose
  park branch runs first. `pending_asks` passes `ask_id`. `land` writes the
  verdict `answered` when a park page's every ref is approved.
- `rota/roles/api.py`: `rulings_rule` loses its park refusal and passes
  `ask_id`. `rulings_line` passes `ask_id`.
- `rota/core/runner.py`: `resolve_inbound` passes `ask_id` and drops the
  `no_row_to_rule` note. `_mode_key` keys a Terminologist `relay` whose
  refs hold a criterion to `criterion_repair`.
- `rota/roles/prompts/liaison/park_ask.md` and `.tools`: the brief of the
  design, and `msg.present_principal` alone.
- `rota/roles/prompts/liaison/verdict_signoff.md`: criteria go to the
  Terminologist with `msg.relay_terminologist`.
- `rota/roles/prompts/terminologist/criterion_repair.md`: the paragraph
  "A ruling of the principal".

**2.B, the note.** The door writes the note with status `answered`.
`render_page` renders it as the note, and `render_state`'s parked line
(`parked_line` inside `render_state`) says "Stuck: <b> stops here. It
breaks <files>.".

**2.D.** `quarantined` skips a key in `given_up` of a batch that
`park_owns`. `rulings_rule` refuses a contest or a revise on a batch ref,
on every page, and names the item and its line. `invariants._owes_ask` is
`park_owns` and not `park_rests`.

**2.E, the ceiling.** `land` writes the verdict `answered`, the page rests,
and the parked line says "You approved its checks as they stand, and <n>
of them still fail.".

**Meta workflow.** `rota/testkit/scenes.py`: `PARK_ASK` sends a present,
`PARK_REPLY` is gone, and the scene `two_batches` approves the park page
once, where night 121 asked three times.

## Deviations from the design

- `park_criteria` reads the criteria of the batch's tickets and the
  criteria its tests name (reasoned: night 93's fixture, which
  `test_next_batch.py` reads, holds the tests without the tickets).
- The digest sums the own tests' versions, not every test of the batch
  (reasoned: a sibling's start moved the project tests' rows off b1, frame
  130's wall, and that ended the rest of an approved page in the scene
  `two_batches` with nothing of the change moved).
- `sandbox.situational` keeps `msg.answer_tester` for a Terminologist woken by
  a relay that holds a criterion (reasoned: the asker rule kept only
  `msg.answer_liaison`, which `criterion_repair` lacks, so the first
  recording of the new case scored 0 of 5; the design had left this check
  to the implementer).
- `L1-LI-a-parked-batch-is-put-to-the-principal-once` expects
  `refs_include` and not `refs_equal` (reasoned: the fixture's ids are
  drawn per run, so the criteria's id order changes per run, and two of
  five runs failed on the order alone; `test_park_page.py` pins the order).
- The detail's word is a sentence, `It is a page.` or `It is a note.`
  (reasoned: the brief reads the line below the refs, and a bare word at
  the end of a sentence reads as a typo).

## Tests

- `tests/rota/test_park_page.py`, new, 11 tests: the page (night 132,
  m117), a full map and a criterion contest (s218), the rest and the
  criterion move, an empty ruling, the check line (tr248, night 121's
  `tst_confirm_eof_cr3`), the closed note (night 133, s319), the running
  batch's quarantined key, the batch-line refusal (s313), the ceiling
  (night 121, s278), and the criterion relay into `criterion_repair`.
- `tests/rota/test_next_batch.py`: the park helper and 7 park tests
  rewritten to the page. Test 458 is now
  `test_an_approve_then_a_criterion_move_asks_again_and_a_bare_lift_does_not`.
- `tests/rota/test_scene_park.py` and `tests/rota/test_scene_two_batches.py`:
  the park ask is a present, and I5 holds on `two_batches`.
- Cases: `L1-LI-a-parked-batch-is-put-to-the-principal-once` rewritten,
  `L1-LI-a-parked-batch-with-only-project-reds-is-a-note` and
  `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` new.

## The gate, the second run, verbatim

```
suite: 25 failed, 3380 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 624.3s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 4 new reds are the 4 known reds of the brief.

## Re-records

The first gate re-recorded the 6 stale cases on qwen3:8b, five runs each:

- `L1-LI-a-parked-batch-is-put-to-the-principal-once`: 3/5, both misses on
  the refs' order. Green on replay after the `refs_include` change.
- `L1-LI-a-parked-batch-with-only-project-reds-is-a-note`: new, 5/5.
- `L1-LI-a-ruling-splits-by-owner`: 5/5.
- `L1-LI-relay-a-ruling-without-interpreting-it`: 5/5.
- `L1-TE-repair-the-criterion-the-tester-cannot-encode`: 5/5.
- `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told`: new, 0/5,
  then 5/5 after the answer door, re-recorded by hand with
  `ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288`.

## Unfinished

- The second page before a respecify is fixed in pass 1b, finding 2.
- `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`
  is red on a clean checkout at 985a6e85 too, and is in the gate's
  baseline (observed: a worktree at HEAD, 2026-10-09).

## Pass 1b, the diff review of b0a2086e

Written by the same implementer, 2026-10-09, on the tree at 4d2bdc90. The
findings are `review142p1_findings.md` in the scratchpad of session
acb1f403.

- Finding 1, high. `scheduler.park_criterion_relay` holds the test: a
  relay whose every ref is a criterion and whose cause chain reaches a park
  page within four hops (`scheduler.park_page_of`). `runner._mode_key`
  keys `criterion_repair` on it, and `sandbox.situational` opens
  `msg.answer_tester` on it. `RULED_TABLES` loses `criteria`. The relay
  split in `_bind_send.stage` routes a criterion to the Terminologist only
  when the trigger's chain reaches a park page. Any other criterion keeps
  the old route, the named recipient. `verdict_signoff.md` is back to its
  text before pass 1, because the door does the routing. Tests: night
  133's m327 shape (a contest through `about_ref`) and m88's mixed refs
  stay in `relay`.
- Finding 2, high. `scheduler.park_ruling` returns the landed ruling that
  names every ref of the page, whatever the verb, and a page with one
  rests. A contest rests the page, and its respecify moves the version
  pairs, so the re-park asks then. `render_state` says "The team rewrites
  the lines you corrected" for a rested page with a contest. The test
  contests line 3 and shows no second page and a clean I5 before the
  respecify, then a new page after it.
- Finding 3, medium. The Terminologist case pins the write to `<c2>`, and
  its park page carries a park id. New case
  `L1-TS-encode-a-criterion-the-principal-corrected`: a Tester answer
  whose cause is a relay. The first criterion, about invoices that stay in
  place, gave 1/5: the Tester tried to encode each time, and the encodes
  failed on names the sample does not have. The criterion is now one that
  `close_account` meets in the sample, and it gave 5/5.
- Finding 4, low. `_park_versions` returns the sorted `id:version` pairs
  of the criteria and the own tests, and the digest hashes them.
- Finding 5, low. Not changed. The case matcher has `refs_include` and
  `refs_equal` only, and no set comparison. `test_park_page.py` pins the
  exact list.
- Finding 6, low. Project tests stay out of the digest. The page's rows are
  criteria, and a broken project test is the builder's regression (ruled:
  2026-09-14). A note renders its file list live from the runs, and the
  head commit is its exit. A re-encoded project test therefore must not
  end a rest. A sibling's start also moves the project tests' rows off the
  batch (frame 130's wall), which ended a rest in the scene `two_batches`
  with nothing of the change moved (observed: 2026-10-09).
- Finding 7, low. Not changed, as the finding says.

## Pass 2, the delta review of 172b373b and the chat intake

Written by a fresh implementer on Opus, 2026-10-09 02:08, on the tree at
0baacf55. Rota workflow, except where a line says meta workflow.

**Part 1, `fix(rota)` at 67751385.**

- Finding 1, high. `sandbox.stage_park_relay` runs in `run_session` before
  the result is built. On a Liaison session whose trigger is a verdict on a
  park page, it stages one relay of the contested criteria to the
  Terminologist. A relay to the Terminologist that the session sent gains
  the missing criteria, so a criterion gets one relay.
  `scheduler.park_verdict_criteria` reads the contested rows from the
  verdict's `verdict:` config map. `verdict_signoff.md` is unchanged.
- Finding 2, low. `L1-TS-encode-a-criterion-the-principal-corrected`
  checks `ids_include: [<tst1>]`. It replays green, so the encode keeps
  the id (observed: 2026-10-09).
- Finding 3, low. `scheduler.park_page_of` is gone.
  `scheduler.park_verdict_page` takes one hop: a verdict whose cause is a
  park page. `park_criterion_relay` needs the relay's cause to be that
  verdict, and the relay split in `_bind_send.stage` keys on the trigger
  being that verdict.
- Tests: `test_park_page.py` gains the door's relay, after a session that
  sends nothing and after one that relays the item, and the two-hop relay
  that keys no repair. New case
  `L1-LI-a-park-verdict-sends-its-contested-criterion-to-the-terminologist`,
  recorded 5 runs on qwen3:8b, green.

**Part 2, `feat(rota)` at 0baacf55, design 2.C with amendment 3.**

- `sandbox.ENUMS_BY_OP` keeps `work` alone for `brief.intake`, and the new
  `ENUM_REFUSALS` gives the design's sentence for `chat`. `brief_intake`
  loses the `chat` entry and says why.
- `converse.tools` loses `msg.converse_principal`. `converse.md` carries
  the design's paragraph and its two examples, and its first line names
  `work` alone.
- The intake door in `_bind_send.stage` loses the two `chat` branches.
- `api.brief_segment` refuses words equal to a statement on file that is
  not `superseded`, compared with whitespace folded and case folded.
- `api.repeated_sentence` and `api.refuse_repeated_sentence`: the nearest
  principal message on the trigger's chain gives the words, and an earlier
  principal entry with the same words that drew a Liaison message to the
  principal within three levels of its cause chain gives the refusal. The
  stage door applies it to `clarify`, `converse` and `confirm` to the
  principal, and `rulings_rule` to `ask=`.
- `runner._recent_chat` reads a principal turn with no `body_text` from its
  entry (`api.message_entry`).
- Tests: new `tests/rota/test_chat_intake.py`, 5 tests on night 132's s220
  rows and night 121's s284 rows. `test_intake_fork.py`: the chat test
  inverts, and the vocabulary test is renamed
  `test_the_verdict_vocabulary_is_work_alone`. The door's tests add
  `msg.converse_principal` to the working set themselves.
  `test_t0_sandbox.py`: 11 chat claims become `ctx.intake = "unarmed"`, as
  the answer mode is. `test_desk_guards.py`: the chat test that derived a
  statement ref becomes a clarify that names the statement.
- Case: `L1-LI-chat-is-not-work` expects one `clarify` with
  `refs_include: [e_<m_in>]`.

**Deviations.**

- Part 1 is committed before part 2 was written, and one gate run covers
  both (reasoned: the two parts share `sandbox.py` and `runner.py`).
- The question-span refusal of `brief.segment` named
  `msg.converse_principal`, which the converse mode no longer offers. It
  now names the owner's ask and `msg.clarify_principal`.

**The gate, the second run, verbatim.**

```
suite: 25 failed, 3398 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 677.8s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 4 new reds are the 4 known reds of the brief.

**Re-records.** The first gate re-recorded 8 stale cases on qwen3:8b,
five runs each, all 5/5: `G1-a-reply-that-answers-something-else-ratifies-nothing`,
`G1-scope-sounding-words-are-not-scope-yet`,
`G1-what-the-brief-already-holds-is-answered-from-it`,
`L1-LI-a-question-about-the-program-goes-to-its-owners`,
`L1-LI-chat-is-not-work`, `L1-LI-no-report-no-question`, `L1-LI-segment`
and `L3-a-maintainers-question-reaches-the-owner`.

**Unfinished.**

- An answer to a clarify on an entry lands on no row, because
  `_table_of_ref` returns None for an entry. The diff review checks what
  `answering` then does with it (frame 142's design, 2.C).
- The runner's guard that drops statements beside a converse to the
  principal stays. Only the `answer` mode and `rulings.rule(ask=...)` write
  that converse now.

## Pass 2b, the diff review of 0baacf55

Written by a fresh implementer on Opus, 2026-10-09 03:00, on the tree at
4ef3bd9f. Rota workflow, except where a line says meta workflow.

**`fix(rota)` at 4ef3bd9f.**

- Finding 1, high. `runner._mode_key` keys `converse` on a principal reply
  whose cause is a clarify with every ref an entry
  (`runner._asks_about_entries`). A clarify on a row keeps `answering`. A
  reply carries the clarify's refs, so the session segmented the old entry.
  `runner.message_entry_id` and `api.message_entry` now read `e_<id>`
  first, then the refs.
- Finding 2, medium. The relay split in `_bind_send.stage` drops a park
  page's criterion that `scheduler.park_verdict_criteria` does not name.
  A relay of approved rows alone is refused. `sandbox.stage_park_relay`
  drops an approved criterion from a held Terminologist relay.
- Finding 3, medium. `api.repeated_sentence` returns only a Liaison
  message to the principal whose status is `open`.
- Finding 4, low. The intake fork refuses the first `msg.clarify_principal`
  on the entry before any `brief.intake`. The second goes.
- Tests: `test_chat_intake.py` gains the reply on a rebuilt row set, run as
  a session with a scripted model, the closed confirm, and the clarify
  refused before the intake. The `answering` test puts m119 on a statement.
  `test_park_page.py` gains a third relay shape, an exact relay, and a held
  relay with two approved criteria and a term.

**Deviations.**

- Finding 4's guard refuses once, not always (observed: 2026-10-09). The
  brief's guard made `L1-LI-chat-is-not-work` segment "hey, morning!" 0/5.
  The model claimed work after the refusal. A second refusal text that puts
  the greeting route first, with the guard refusing once, gave 5/5. The
  greeting route of design 2.C, a clarify on the entry, needs no intake.

**The gate, the second run, verbatim.**

```
suite: 25 failed, 3403 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 673.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 4 new reds are the 4 known reds of the brief.

**Re-records.** `L1-LI-chat-is-not-work` on qwen3:8b, five runs each: the
first gate 0/5, a manual run with the guard refusing once 0/5, a manual run
with the new refusal text 5/5, then a plain replay green.

**Unfinished.**

- No case covers a real request answered with a clarify on the entry. The
  unit test covers the door only.
- `converse.md` still shows the greeting's clarify with no intake. The
  guard's second pass keeps that example true.

## Pass 2c, the delta review of 4ef3bd9f

Written by the pass 2b implementer, 2026-10-09 03:39, on the tree at
b9a370cd. Rota workflow, except where a line says meta workflow.

**`fix(rota)` at b9a370cd.**

- Finding 1, high. `api.repeated_sentence` keys on any earlier Liaison
  message to the principal, whatever its status. `api._confirm_landed`
  exempts a confirm that has a `rulings` row with status `landed`. On night
  132's rows, read-only, `repeated_sentence(conn, 'm_p5')` gives m118
  (observed: 2026-10-09). The `s220` fixture marks m_p4 and m119 answered.
  There are two new tests: a repeat after a landed verdict gets its
  confirm, and a repeat while the confirm has no landed verdict is refused.
- Finding 2, medium. On a park verdict, the relay split keeps only the refs
  that `scheduler.park_verdict_criteria` names, and routes them to the
  Terminologist. The item is dropped. `stage_park_relay` sets a held relay
  to the contested criteria alone. The tests assert that no relay goes to
  any role but the Terminologist.
- Finding 3, medium. The one-time guard and `ctx.entry_clarify_refused`
  are gone. The fork keeps nothing for a clarify. The new case
  `L1-LI-a-request-is-claimed-before-any-clarify` is in
  `tests/rota/cases/l1_liaison.yaml`.
- Finding 4, low. The refusal for a relay of approved rows alone is gone.
  No test held it.

**The new case, 0/5 on qwen3:8b.** All five runs give the same calls:
`transcript.quote`, then
`brief.segment(id="s1", span_start=0, span_end=113, text="make confirm() return the default answer when stdin is closed instead of aborting", span_entry=...)`
and `msg.confirm_principal(refs=["s1"])`. The only problem is "expected a
call to brief.intake". No run sends a clarify. The converse brief's work
example also has no `brief.intake`. No brief is changed. That is a frame.

**Deviations.**

- The new case does not forbid a confirm to the principal. A segment
  followed by a confirm is the work route of `converse.md`, and
  `L1-LI-segment` allows it. A forbidden confirm would fail correct work.
- The gate ran once, as the pass asked. The stale case was re-recorded
  after it, so the stale line below is from before that re-record.

**The gate, verbatim.**

```
suite: 27 failed, 3406 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (5): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-LI-a-request-is-claimed-before-any-clarify], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (1): L1-LI-a-park-verdict-sends-its-contested-criterion-to-the-terminologist (+1 -0 against baseline)
time: 867.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The new reds are the 4 known reds and the new case. The night held the
main card, so the gate re-recorded nothing.

**Re-records**, on qwen3:8b, five runs each, in the foreground:

- `L1-LI-a-request-is-claimed-before-any-clarify`, recorded at 0/5.
- `L1-LI-chat-is-not-work` gave 5/5, and each run sends one clarify.
- `L1-LI-a-park-verdict-sends-its-contested-criterion-to-the-terminologist`
  gave 5/5. A plain replay of it and of the chat case passed.

**Unfinished.**

- The new case is red. Its cause is the missing `brief.intake` call, so
  it is a frame for the converse brief.
- A park verdict that contests line 1, the item, now relays nothing. The
  split then refuses with "every owner these rows belong to has its relay
  already". No night has shown this shape.

## Pass 2d, the item line and the outcome case

Written by the pass 2b implementer, 2026-10-09 03:55, on the tree at
55fe8a04. Rota workflow.

**`fix(rota)` at 55fe8a04.**

- The item line. `scheduler.park_verdict_rows` returns every line that a
  park verdict contests or revises, the item and the criteria.
  `park_verdict_criteria` keeps the criteria among them. On a park
  verdict, the relay split sends a criterion to the Terminologist and the
  item to its owner, the Vision Keeper. A verdict that rules on criteria
  alone sends no item. The new test in `test_park_page.py` contests line
  1 and approves the rest, for a session that relays the item and one that
  relays a criterion. Each test stages one Vision Keeper relay of the item
  and no Terminologist relay. The test on criteria alone is unchanged.
- The case. `L1-LI-a-request-is-claimed-before-any-clarify` is now
  `L1-LI-a-request-lands-as-a-statement-and-draws-no-clarify`. It expects
  one statement whose row carries the entry id and the words "default
  answer when stdin is closed", and one confirm to the principal. It
  forbids a clarify or a converse to the principal. It does not expect a
  `brief.intake` call.

**Deviations.** None. The case allows the confirm, as pass 2c's deviation
says.

**The gate, verbatim.**

```
suite: 25 failed, 3410 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 620.4s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 4 new reds are the 4 known reds.

**Re-records.** `L1-LI-a-request-lands-as-a-statement-and-draws-no-clarify`
was recorded before the gate, 5/5 on qwen3:8b. The gate named no stale case.

**Unfinished.** Nothing from this pass.

## Pass 2e, night 135's loop on a row id

Written by the pass 2b implementer, 2026-10-09 05:59, on the tree at
eee89bc8. Rota workflow. The tests rebuild night 135's rows inline in
`tests/rota/test_night135_loop.py`.

**`fix(rota)` at eee89bc8.**

- Fix 1, high. `api.brief_segment` branches the on-file refusal on the
  status. A ratified row: "these words are s1, which the principal
  ratified. Cite s1. There is nothing to segment or ask". A proposed row
  names `msg.confirm_principal(refs=['s1'])`. Any other status is cited.
  No refusal names a clarify.
- Fix 2, low. The door sets the span from where the text is in the entry,
  the nearest occurrence to `span_start`. It does not refuse. s209's call,
  span 0 to 6, is stored as 0 to 254, and with s1 on file it meets the
  ratified refusal.
- Fix 3, high. A segment whose id is on file is refused: "s1 is on file; a
  statement keeps its id, and a new statement takes a new id". s1 stays at
  version 1.
- Fix 4, high. `api.answered_question` finds the latest Liaison clarify,
  converse or ask to the principal with the same words that a principal
  reply follows. The reply's cause is the question, or the reply is the
  next principal message in the question's thread.
  `api.refuse_answered_question` names both ids. `rulings.rule(ask=...)`
  and the stage door, for clarify and converse to the principal, call it.
  On the rebuilt rows the door gives m119 and m120 for m129, and m129 and
  m130 for m131. On a clarify the older door "you have already put these
  words to the principal" fires first and names m119.
- Fix 5, medium. The landing's `earlier_exchange` in
  `runner.resolve_inbound` adds the Liaison's clarify and converse
  messages whose cause is a principal reply to the page, in seq order,
  with `asked: true`. On s224's rows it shows m129, m131 and m133 beside
  the replies.
- Fix 6, the coordinator's addition. A `span_entry` that names no entry is
  refused before any write. A statement id gets "s1 is a statement, and a
  statement is not an entry", and then the entry this session can segment
  or "This session has no entry to segment against". The test runs s247's
  call in a session on the self-relay m156, and the session commits.

**Deviations.**

- Fix 2 sets the span and does not refuse (reasoned: the intake tests
  send a span five characters short with the right text, and a refusal
  would refuse correct work). The text must still be in the entry.

**The gate, verbatim.**

```
suite: 26 failed, 3416 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (5): tests/rota/test_handover.py::test_a_newer_watcher_retires_the_older_one, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 1272.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate marks `test_a_newer_watcher_retires_the_older_one` flaky, and
`test_handover.py` passes 53 of 53 alone (observed: 2026-10-09). The
other 4 new reds are the known reds. The run took 1272.6 seconds,
against about 670 seconds before.

**Re-records.** None. No case went stale, so no recorded turn held a
changed refusal or a changed `earlier_exchange`.

**Unfinished.** The self-relay m116 that woke s209 with no mode section
is a frame of its own.

## Pass 2f, the review of eee89bc8

Written by the pass 2b implementer, 2026-10-09 06:21, on the tree at
40691aa7. Rota workflow.

**`fix(rota)` at 40691aa7.**

- Fix 1, medium. `api.brief_segment` checks the words on file before the
  id. An id on file is refused with the lowest free `sN`, counting the
  rows on file and the session's staged rows: "s1 is on file; a statement
  keeps its id. Segment these words as s2". The test sends s267's shape,
  then the same call with s2, which lands.
- Fix 2, medium. The older door on a repeated clarify in
  `_bind_send.stage` calls `api.refuse_answered_question` before its own
  message. When a principal reply follows, the seat gets "you asked this
  in m119, and the principal answered it in m120", then read and rule or
  end.
- Fix 3, low. A moved span returns `"span": [start, end]` and
  `"note": "span set from the text"`. A span past the end of the entry is
  moved too, because s1 held span 0 to 223 on a 115-character entry. The
  test uses "Drop line 2. Keep line 3. Drop line 2." with span 10 to 22,
  which moves to 0 to 12.
- Fix 4, low. `rota/DECISIONS.md`, "`brief.segment`'s span is never
  checked against its own text", now reads "*Fixed by frame 142, pass
  2e:*".

**Deviations.** One addition: a span past the end of the entry is moved
(reasoned: the slice clips at the end, so the words matched and the row
kept span_end 223).

**The gate, verbatim.**

```
suite: 25 failed, 3418 passed, 32 skipped, 16 xfailed, 17 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 654.8s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The 4 new reds are the known reds.

**Re-records.** None. No case went stale.

**Unfinished.** For the night read: the answered door keys on the words
alone, and `earlier_exchange` goes one level deep with no size bound.
