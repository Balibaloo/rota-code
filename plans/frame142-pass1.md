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

- Between a criterion contest landing and the Terminologist's respecify,
  the closed page does not rest, so `park_ask` can open a second page on
  the same rows before the move lifts the key (reasoned: the digest counts
  the close; not observed on a night).
- `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`
  is red on a clean checkout at 985a6e85 too, and is in the gate's
  baseline (observed: a worktree at HEAD, 2026-10-09).
