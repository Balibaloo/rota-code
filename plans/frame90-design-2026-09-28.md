# Frame 90, the Architect cannot file a finding: the read and the design

Written by session b4768744, rota-66, on 2026-09-28. Revision 1, before the
design review. Rota workflow unless a line says otherwise.

## 1. What night 95 shows, read from the code and the database

The night's record is `plans/archive/night95-walk-2026-09-28.md`, section 2.
This read adds the causes.

1. **Why the Architect woke at all.** `needs_structural_review` in
   `rota/core/lifecycle.py` counts a constraint with no binding as global.
   Constraint zero, `k0`, has no binding, so every batch with a pass at its
   head wakes the Architect, whether or not a constraint binds the diff
   (observed: `constraints` and `constraint_bindings` in
   `.rota/clickI_night95.db`, `k0` has 0 bindings and the other 11 have 2
   each, 2026-09-28; `rota/core/lifecycle.py` lines 318 to 330 at `e5e067d`).
   On night 95 no constraint bound `src/click/utils.py`. The Architect was
   woken to check constraints that did not reach the change.
2. **Why the finding call was refused, and why the lists differ.** The door
   `_must_exist` in `rota/roles/api.py` names at most six rows of the table
   (`LIMIT 6`, line 307). The refusal that listed 6 rows against the 12 of
   `model.consult` is that limit, not a second constraint set (observed:
   `rota/roles/api.py` at `e5e067d`, 2026-09-28). The refusal says "no
   constraints row with id='echo_json_compact'". It does not say that the id
   is a criterion, and it does not name what to do when no constraint binds
   the diff.
3. **The id refusal corrected itself.** The first call used a test id as the
   finding id and the uniqueness door refused it. The second call used
   `fnd_001`, and only the constraint refusal remained (observed:
   `tool_calls` of s144, seq 6 and 7, 2026-09-28). Not a fault of this frame.
4. **What the brief says.** `rota/roles/prompts/architect/structural_review.md`
   says `findings.find` per constraint checked, and names no exit for a diff
   that no constraint binds (observed: the brief at `e5e067d`, 2026-09-28).
   A satisfied finding on `k0` is legal at the door, and `finding_review`
   excludes `k0`, so that finding stops the `structural_review` predicate and
   wakes nobody (reasoned: `findings_find` and `finding_review` at
   `e5e067d`, not run).
5. **The empty answer.** `msg.answer_developer` is in
   `structural_review.tools`. The wake was a tick, so `ctx.trigger` was None
   and no question existed (observed: `sessions` s144, `trigger_msg` None,
   2026-09-28). The message binder in `rota/core/sandbox.py` makes an
   answer's words optional, and no door asks whether anything was asked. The
   answer landed with `body_text` None and `cause_id` None (observed:
   `messages` m62 to m65, 2026-09-28). The Developer woke on `message`
   `answer` with empty `wake_refs` and rewrote the criterion's code four
   times (observed: the same record, section 2).

Verdict: the wall has two doors that do not say the exit, and one brief
that does not name it. The wake is by design and stays.

## 2. The design

Four changes, one implementer pass, one diff review, one night shared with
frames 88 and 86.

1. **`findings.find` names the exit.** When `constraint_id` is not a
   constraints row, the door says which table holds that id, a criterion or
   a test, and names every constraint id, not six. Then it says: a criterion
   is the Critic's, and a finding names a constraint from `model.consult`;
   when no constraint binds the diff, file `k0` satisfied with a changed
   file as the grain. Site: `findings_find` in `rota/roles/api.py`, before
   `_must_exist`.
2. **The brief names the same exit.** One paragraph in
   `structural_review.md`: when `model.consult` returns no constraint that
   binds a file of the diff, file one finding, `k0`, `satisfied`, with a
   changed file as the grain. That row is the record that the review ran.
   Do not answer the Developer, because nothing asked.
3. **An answer with no question is refused.** In the message binder, `verb
   == "answer"` with `ctx.trigger` None raises: "nothing asked you this
   session; an answer replies to a message, and this wake is a tick; a
   review's record is findings.find". Site: the door block in
   `rota/core/sandbox.py` beside the Terminologist's answer door. And
   `msg.answer_developer` leaves `structural_review.tools`, because the
   brief never names it and the door now refuses it there.
4. **Two tests and one recorded case.** A unit test in
   `tests/rota/test_t0_sandbox.py` holds change 3 on a stub. A unit test
   holds change 1's refusal text on a criterion id. One new case in
   `tests/rota/cases/l1_architect.yaml`, on night 95's shape: `k0` plus two
   bound constraints whose bindings do not meet the diff, a pass at the
   head, and the expectation that `findings.find` lands with `k0` satisfied
   and no message is sent. Runs 5, pass 4. The recorder line from
   `plans/operating-facts.md` carries the model.

Not this frame: `k0` counting as global in `needs_structural_review`. With
changes 1 and 2 the Architect's session on a diff nothing binds costs one
call and files one row, which is the record Roman asked the night to show.
A predicate change carries its own walk.

## 3. The ends-when, clause by clause

- The finding call lands on the first try in a recorded case: change 4.
- The door names the ids it wants in a way the model follows: change 1, and
  the case shows it.
- An empty answer is refused with the reason: change 3.
- The two constraint lists agree: change 1 names every constraint id.
- A night shows a finding filed: the `k0` row. **A night shows
  `tick:finding_review`: only a violated finding wakes the Critic, and on
  night 95's shape no constraint binds the ticket's file, so no finding is
  violated.** That clause is frame 88's proof, and it needs a fixture where
  a constraint binds the file the ticket changes. Recommended to Roman at
  the night's plan: accept the `k0` row as this frame's proof, and give
  frame 88 a night on a ticket that a constraint binds.

## 4. Prices

From the anchors: the read, 40k, spent by this session as one-line doors.
One implementer pass on Opus, 60k. One diff review, 50k. The night, shared.
