# Frame 88 design record, revision 1 (2026-09-27)

Rota workflow, the seats on click. Written by session 213e58fd, meta workflow,
from `plans/archive/frame88-scope-2026-09-27.md` and Roman's ruling of
2026-09-27 (ruled: only the Critic can reopen a green, signed-off batch; a
finding filed after the Critic's pass goes to the Critic first, and only the
Critic's fresh verdict sends the Developer back).

## The fault

On night 94 `bg_1` passed the Critic at attempts 4 and 5. The Architect filed
`fnd_1` against the constraint `echo`, which the Critic had falsified in s78.
The finding woke the Developer twice, the changes broke the imports, and the
batch never merged (observed: the scope read, sections 1 to 3, 2026-09-27).
Every Architect finding comes after a Critic pass, because the Architect's
wake fires only on a pass at the head commit. So the ruling routes every
post-pass finding through the Critic.

## The route

1. `finding_violated` in `rota/core/predicates.py` gains one condition: a
   Critic ruling `upheld` on the finding at the head commit. The wake kind
   `tick:finding_violated`, its refs and the Developer's brief stay as they
   are.
2. A new predicate `finding_review` wakes the Critic on a violated finding at
   the head commit that has no ruling yet. Wake kind `tick:finding_review`,
   refs `(batch_id, finding_id)`. It counts under the attempt cap like every
   tick wake.
3. A new Critic mode, `critic/finding_review.md` and its `.tools`: the tools
   are `findings.load`, `model.load`, `code.read`, and one new op
   `findings.rule(finding_id, ruling)` with `ruling` in `upheld` or
   `dismissed`, and a reason. `findings.load` in this mode shows the challenge
   verdict on the finding's subject beside the finding, so the Critic sees
   its own falsification (open question 1: it reaches the Critic; a
   mechanical dismissal is not a fresh verdict).
4. `findings.rule` writes one row in a new table `finding_rulings`:
   `finding_id`, `commit_sha`, `ruling`, `reason`, `session_id`, `at`. Nothing
   else moves. A `verdicts` row would overwrite the pass on the same commit,
   and `failed_criterion` cannot name a constraint (open question 2).
5. `mergeable` skips a violated finding with a `dismissed` ruling at the head
   commit. An `upheld` ruling leaves the finding as it is, and the Developer
   wakes through step 1.
6. The Architect's `escalate` mode keeps `findings.find` (open question 3).
   `findings.find` keeps overwriting a row by id across commits; the ruling is
   keyed by finding and commit, so it reads correctly after an overwrite. The
   lost finding at `aeef7c0c` is recorded as a separate question and not
   repaired here (open question 4).

## The format fault

The ticket says `indent=2`, the test expects compact output, and the
criterion says nothing on the format. The fix is the fixture's ticket
sentence, which moves no recorded prompt (observed: the scope read, section
5). It is in this frame, as its second part, because Roman's second step is
"so frame 33 gets its merge" and a night that proves the route must also
reach the merge (this differs from the scope read's recommendation on open
question 5, reasoned: the frame exists for the merge).

## Prompts that move

None required. `L1-AR-find-against-a-constraint` moves only if the
Architect's `structural_review.md` lines 22-23 change, and they do not. One
new Critic case is recorded live for the new mode. No line in `critic/base.md`
or `critic/review.md` moves, and `verdicts.emit` gains no parameter.

## Tests

- A predicate test: a violated finding at the head commit with no ruling
  wakes the Critic and not the Developer; with `upheld` it wakes the
  Developer; with `dismissed` it wakes nobody and `mergeable` holds.
- An op test: `findings.rule` refuses a finding not in the wake's refs, and a
  ruling outside the two words.
- One recorded Critic case for the new mode, on the night 94 shape: a finding
  on a falsified constraint, the Critic dismisses it.

## Ends when

The predicate and op tests hold, the new case records green, the fixture
sentence names the format, the gate is clean against the stored baseline,
and a night from a worktree at the closing commit shows a post-pass finding
reach the Critic and `bg_1` merge or fail on a test. Priced: one implementer
pass, about 80k on Opus; one diff review per pass, about 50k each; one night.

## Open for the design review

1. Does the Critic's `finding_review` session count toward the batch's attempt
   cap, or is it free? Recommended: it counts under the tick counter for the
   wake kind and not the attempt cap, because it writes no code.
2. Does a `dismissed` ruling at commit A hold at commit B when the finding is
   re-filed unchanged? Recommended: no, a ruling is per commit, and a
   re-filed finding at a new commit reaches the Critic again.

## Revision 2 (2026-09-27, after the design review)

The review on Opus 5.5 confirmed six findings (observed: the review's probes
on the graph, the register and night 94's rows, 2026-09-27). Revision 2 folds
them. Where it differs from revision 1, revision 2 holds.

1. **The Critic's tools and the op.** The mode's tools are `findings.load`,
   `challenge.load` and `code.read`. Not `model.load`: `model` is contactable,
   and a Critic read on it derives a contact to the Architect, which is a
   change to the composition. The op is `verdicts.rule(finding_id, ruling,
   reason)`, on the Critic's own `verdicts` artefact, so the Architect's
   `findings` keeps one writer. The table `finding_rulings` belongs to that
   artefact. `challenge.load` already shows the falsification.
2. **The bound.** The rounds of `finding_violated` count the distinct
   `commit_sha` in `finding_rulings` where `ruling = 'upheld'` for the
   batch's findings, against `loop_cap`. The old count over `findings`
   rows never bound, because `findings.find` overwrites by id.
3. **One finding at a time.** `finding_violated` fires only when no violated
   finding at the head commit lacks a ruling, so the Critic rules on every
   finding before the Developer sees any.
4. **Step 2's wording.** The Critic's wake counts in `tick_attempts` under
   `critic|tick:finding_review|<batch>,<finding>` by `note_dispatch`, and
   never in `test_runs.attempt`.
5. **The cockpit.** The findings view in `rota/cockpit/inspect_api.py`
   shows the ruling beside a violated finding.
6. **The existing test.** `tests/rota/test_predicates.py` near line 1836
   expects `finding_violated` on a violated finding with no ruling. That
   test gains an `upheld` row.
7. **The walk's ends-when.** The night must show `tick:finding_review` in
   `sessions`. A night with no post-pass finding is recorded as "the route
   did not run", and it proves nothing about the route.

Files the implementer touches: `rota/roles/prompts/critic/finding_review.md`
and `.tools`, `rota/design/graph.json` for the `findings.load` read edge,
`rota/roles/api.py` for `verdicts.rule`, `rota/core/sandbox.py` for the op's
enum, the schema for `finding_rulings`, `rota/core/predicates.py` for
`finding_review` and `finding_violated`, `rota/core/lifecycle.py` for
`mergeable`, `rota/cockpit/inspect_api.py`, `probes/gauntlet_click.sh:79`,
and the tests. Moved cases: 0. One new Critic case records live.
