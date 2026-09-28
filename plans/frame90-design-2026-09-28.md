# Frame 90, the Architect cannot file a finding: the read and the design

Written by session b4768744, rota-66, on 2026-09-28. Revision 2, after the
design review on Opus (about 107k, 72 tool uses), which returned 11
confirmed findings and 1 plausible. Revision 1 is at `c9e08eb`. Rota
workflow unless a line says otherwise.

## 1. What night 95 shows, read from the code and the database

The night's record is `plans/archive/night95-walk-2026-09-28.md`, section 2.
This read adds the causes.

1. **Why the Architect woke at all.** `needs_structural_review` in
   `rota/core/lifecycle.py` counts a constraint with no binding as global.
   Constraint zero, `k0`, has no binding, so every batch with a pass at its
   head wakes the Architect, whether or not a constraint binds the diff
   (observed: `constraints` and `constraint_bindings` in
   `.rota/clickI_night95.db`, `k0` has 0 bindings and the other 11 have 2
   each, all on `src/click/globals.py`, `__init__.py` or `_utils.py`;
   `batch_touch` of `bg_1` names `src/click/utils.py`; the design review,
   2026-09-28). `k0` is written at onboarding, so the binding branch of that
   function is dead in every onboarded project, and every passed batch needs
   a finding before it merges (observed: the review's probe of
   `mergeable`, 2026-09-28). The `k0` row is therefore the normal case, not
   an edge case.
2. **Why the finding call was refused, and why the lists differ.** The door
   `_must_exist` in `rota/roles/api.py` names at most six rows of the table
   (`LIMIT 6`, line 307). The six named are the first six by id, and the six
   missing sort after them (observed: the review ran the query on the night
   database, 2026-09-28). The refusal does not say that the id is a
   criterion, and it does not name what to do when no constraint binds the
   diff.
3. **Where the two wrong ids came from.** The wake pushed `batches.expect`,
   and its `tests` list holds the pair `{"id": "inh_023c4d92",
   "criterion_id": "echo_json_compact"}`. The Architect copied that pair as
   its finding id and its constraint id (observed: s144 turn 1, the review,
   2026-09-28). The wake also pushed `model.consult` with no grains, which
   listed all 12 rows with no binding column, so the model could not see
   that none binds the diff (observed: the same turn).
4. **What the brief says.** `rota/roles/prompts/architect/structural_review.md`
   says `findings.find` per constraint checked, and names no exit for a diff
   that no constraint binds (observed: the brief at `e5e067d`, 2026-09-28).
   A satisfied finding on `k0` is accepted at the door, stops the
   `structural_review` predicate at that head, wakes nobody, and leaves the
   batch mergeable (observed: the review called `findings_find` and ran the
   predicates on a copy of the night database, 2026-09-28).
5. **The empty answer.** `msg.answer_developer` is in
   `structural_review.tools`. The answer edge from the Architect to the
   Developer has no prose field, so a body of None is the normal shape of
   that message (observed: the graph's answer edges, 14 of 16 carry no
   prose, the review, 2026-09-28). The fault is the cause: the wake was a
   tick, `ctx.trigger` was None, no question existed, and the message landed
   with `cause_id` None (observed: `sessions` s144 and `messages` m62 to
   m65, 2026-09-28). The Developer woke on `message` `answer` with empty
   `wake_refs` and rewrote the criterion's code four times (observed: the
   night's record, section 2). An answer-only session counts as committed,
   so the committed count does not show this stall (observed: s144
   `committed` 1, the review, 2026-09-28).
6. **A violated finding on an unbound constraint is accepted today.** The
   door checks that the grain is a changed file, and not that the constraint
   binds the grain. On the night's database `findings_find(constraint_id=
   'sentinel', status='violated', grain='src/click/utils.py')` was accepted,
   and the copy then woke the Critic on `tick:finding_review` (observed: the
   review's probe, 2026-09-28). Only a correct model does not file one.

Verdict: the wake pushed the wrong ids and hid the bindings, the door does
not name the exit, the brief does not name it, and one tool in the mode's
list sends a message that nothing asked for. The wake by `k0` is by design
and stays.

## 2. The design

Five changes, one implementer pass, one diff review, one night shared with
frames 88 and 86.

1. **`findings.find` names the exit and refuses an unbound violation.** The
   constraint check moves out of `_must_exist` into `findings_find`, after
   the batch check. When `constraint_id` is not a constraints row, the door
   says which table holds that id when one does, a criterion or a test, and
   names the constraints that bind the batch's changed files, from
   `constraints_for_grains(conn, batch_files(...))`. When that set is `k0`
   alone, the door says: no constraint binds this diff; file `k0` satisfied
   with a changed file as the grain. When `status` is `violated` and the
   constraint does not bind the grain's file, the door refuses and names
   the constraints that do. Lists cap at 20 ids, then "and N more".
2. **The wake pushes what the rule needs.** For `structural_review`, the
   pushed `model.consult` carries `grains` set to the batch's changed files,
   so the Architect sees the bound set and nothing else. The pushed
   `batches.expect` drops its `tests` list for this mode, because the pair
   it carries is the pair the model copied. Site: the mode's push list,
   found with the map tool.
3. **The brief names the exit.** One paragraph in `structural_review.md`:
   when the constraints in range are `k0` alone, file one finding, `k0`,
   `satisfied`, with a changed file as the grain. That row is the record
   that the review ran. It does not name any message.
4. **`msg.answer_developer` leaves `structural_review.tools`.** An unlisted
   tool is not bound. No door on the answer verb: the Architect's
   `exhausted` mode answers the Developer from a tick wake on purpose, and
   `rota/core/sandbox.py` line 432 already rules that a wake with no message
   behind it narrows nothing.
5. **Tests and recorded cases.** A unit test in `tests/rota/test_t0_sandbox.py`
   or the api tests holds change 1's three refusals: a criterion id, a test
   id, and a violated finding on an unbound constraint. A unit test in
   `tests/rota/test_predicates.py` on the night's shape holds that a `k0`
   satisfied finding stops `structural_review` and wakes no Critic, and that
   a violated finding on a bound constraint wakes `tick:finding_review`.
   One new case in `tests/rota/cases/l1_architect.yaml`, on night 95's
   shape: `k0` plus two bound constraints whose bindings name files away
   from the `repo.edit` file, a pass at the head, `tick: structural_review`,
   and the expectation `findings: {count: "1..1", text_includes: ["k0",
   "satisfied"]}` and `messages: []`. Runs 5, pass 4. The existing
   `L1-AR-find-against-a-constraint` re-records, because the brief and the
   push move its prompt. The recorder line in `plans/operating-facts.md`
   carries the model.

Not this frame: `k0` counting as global in `needs_structural_review`. With
changes 1 to 3 the Architect's session on a diff nothing binds costs one
call and files one row. A predicate change carries its own walk.

## 3. The ends-when, clause by clause

- The finding call lands on the first try in a recorded case: change 5.
- The door names the ids it wants in a way the model follows: change 1, and
  the case shows it.
- An empty answer is refused with the reason: change 4 removes the tool, so
  the call is not bound in this mode. The empty body was never the fault.
- The two constraint lists agree: change 1 names the bound set, and change
  2 makes `model.consult` show the same set.
- A night shows a finding filed: the `k0` row. A night shows
  `tick:finding_review`: with change 1, a violated finding needs a
  constraint that binds the changed file, and on night 95's ticket none
  does. The unit test of change 5 shows the Critic's wake on the shape.
  Recommended to Roman at the night's plan: accept the `k0` row and the
  unit test as this frame's proof, and give frame 88, the finding goes to
  the Critic, a night on a ticket that edits `src/click/_utils.py` or
  `src/click/__init__.py`, which the bound constraints name.

## 4. Prices

From the anchors: the read, about 45k, this session. The design review,
107k on Opus, observed. One implementer pass on Opus, 80k with the push
change. One diff review, 50k. The night, shared.
