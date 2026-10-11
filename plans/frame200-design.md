# Frame 200 design: the build loop

Status: drafted 2026-10-11 by session 84ce0759 from the scope report
`plans/frame200-scope.md`. Design review on Opus, 2026-10-11 06:23, `plans/frame200-design-review.md`: do not start as written, start after the fixes in the section below. Rota workflow.

## The seam

Three batches were read turn by turn: night 138's b_3 and night 139's
bg_3, both `version_option show_python`, and night 138's b_1, `echo_json`
(`plans/frame200-scope.md`, sections 1 to 3). The loop has one shape. The
Tester writes a test that applies the project's decorator factory to a
local plain function and then calls or invokes that function, so the
test never runs the option the criterion names. The Developer sees the
test as wrong, challenges it, and then writes the product to fit it,
because the end-of-work note in the same result says "the change comes
first". The challenge is stamped answered with nothing, and the
Architect's answer carries refs and no words. Three interviews of the
seats in their contexts say the seats knew the fact and followed the
nearest instruction (section 6).

## Five changes

Section 7 of the scope prices each. The design takes five and leaves
three.

1. **The factory door reads the call shape** (O2a). `tests.encode`
   refuses a test that applies a project factory's decorator to a local
   `def` with no `command` or `group` above it and then calls that `def`
   or passes it to `.invoke`, and a factory's return used as an argument
   of a call that does not decorate. The refusal states the fact: the
   decorated name is a plain function, and calling it never runs the
   option. No shape in the refusal (ruled: 6b52a09d). Site:
   `rota/roles/api.py`, `_factory_misuse` and `_plain_invoked`. Prompts
   move: none.
2. **A landed challenge closes the write doors for that session** (O3a).
   After the session sends `msg.challenge_tester`, `code.write` and
   `code.commit` refuse with the fact: the session challenged the test,
   and a change now builds on the disputed test. The empty-commit note at
   `api.py:12626-12630` drops its "the change comes first" branch when
   the session has sent a message. The interview of s274 turn 12 named
   that note as the line it obeyed. Site: `rota/roles/api.py`. Prompts
   move: none. Two Developer replays may change where they write after
   their challenge; the implementer names them.
3. **The answer brief ends a wordless answer that leaves the test
   wrong** (O4a). `developer/answer.md` gains one branch: when the answer
   holds no words and the session reads the test as wrong, say so in one
   sentence and end, and do not change the code to fit the test. Site:
   `rota/roles/prompts/developer/answer.md`. Prompts move: 1 case,
   `L1-DV-apply-the-answer-and-carry-on`, plus one new case on s282's
   turn. 2 records.
4. **Frame 115's row route, with a branch for a test** (O5a).
   `architect/escalate.md` gains "the constraint holds": `decisions.author`
   a row, then answer with its ref; an answer whose refs add no row is
   refused, and the refusal names `decisions.author`; `_resolve_refs`
   shows a `decisions` row's text in the Developer's wake; and an
   escalation about a test gets a row that names the test line that does
   not encode the criterion. This is frame 115's recommendation of
   2026-10-02 19:05, which the history read placed inside law 2, and the
   scope's count tests it: 10 of 10 Architect answers to the Developer
   over the three batches held no words. Sites: `architect/escalate.md`,
   `rota/core/sandbox.py`, `rota/roles/api.py`. Prompts move: 1 case,
   `L1-AR-route-an-escalation`, plus one new case. 2 records.
5. **Frame 174's stamp** (O5b). `session_commit` in `rota/core/db.py`
   leaves a challenge or an escalation `unresolved`, with a note, when the
   woken session sent no message caused by it. A decision row alone is
   not an answer. The once-guard on the Architect's `unresolved` tick
   must stop a loop. Site: `rota/core/db.py`. Prompts move: none.

Left out: the Tester brief lines O1a and O1b, because the interviews show
the seats knew the fact, and O1b touches the black-box rule, a
composition line. O3b, the cap step, waits for a night on change 2.

## The review's fixes, folded in (2026-10-11 06:30)

Each replaces the item it names. The review's sections hold the evidence.

1. Change 1 names both forms: the `@` form and the call form
   `f(...)(local_def)`, which all 11 Tester bodies of night 139 use, and a
   factory's return called with no function argument. It keeps the
   scope's limit: a factory that adds an option, read as a factory whose
   return or inner decorator is `option(...)`, `argument(...)` or
   `_param_memo`, so `pass_meta_key` and `make_pass_decorator` stay
   admitted. `.invoke` is refused on a runner receiver only, as
   `_plain_invoked` does. 0 of 537 recorded Tester bodies and 0 of 25
   clickI test files meet the refusal.
2. Change 2 also moves two refusals in `rota/core/sandbox.py`: when
   `_sent_this_session(ctx, "tester", "challenge")` holds, `_code_step`
   and `_waits_refusal` give `END_STEP`, and the end-of-work note says
   only that the session has sent its message and ends. 0 recorded cases
   move: in 0 of 10 challenge cases does a write follow the challenge.
3. Change 3 fires only when the session challenged or escalated about
   this test, and a guard case is added: a wordless answer with a right
   red test still expects `code.write` and `code.commit`.
4. Change 4's site for `_resolve_refs` is `rota/core/runner.py:2012-2113`.
   The route to the Tester (ruled: Roman, 2026-10-11 06:30, the
   recommended of three options): the Developer's answer mode gains
   `msg.challenge_tester`, and a challenge whose refs add a decision row
   does not count against the per-criterion cap `LANDED_CHALLENGES`. No
   new edge.
5. Change 5 is limited to a session that sent nothing caused by the
   trigger and wrote no receipt on a row the trigger refs; a decision row
   that cites the trigger counts as a receipt. The note's text:
   `unresolved: the woken session sent nothing and wrote no row that
   cites this message`. Frame 174's baseline is re-counted under this
   definition before pass 2.
6. The measure: the wordless-answer count and the no-reply count are
   queries on `messages`, as the review's section 6 writes them; the
   commit-after-challenge count is a query on `tool_calls` and `receipts`
   plus a read of the answer-mode turn; the test count is a read of the
   stored versions in `turns`.
7. Order: pass 1 is changes 1 and 2 with the two `sandbox.py` refusals;
   pass 2 is change 5 first, then 3, then 4 with the ruled route. One
   night at the end, and its third request avoids frame 202's batch
   shape, or the residue rule names frame 202.

## Why not the other options

## Passes

- Pass 1: changes 1 and 2, both doors in `api.py`, 0 re-records, with
  the encode and Developer door tests. One diff review.
- Pass 2: changes 5, 3 and 4, in that order, 4 records. One diff review,
  the last before the walk.
- About 330k in agents with the reviews, 6 cycles, then one night with
  three requests from a worktree at the closing commit.

## What stays its own frame

- Frame 182: no second `tests_missing` wake for c1 and c2 on night 138;
  the site is the predicate and the scheduler.
- Frame 194: `named_here` reads `surface_refs`; one door line on another
  file pair, and it can run beside these passes.
- A new frame, 202: a criterion whose text names one callable and whose
  surface ref names another, night 139's c1, which moved s250 and s274.
  The cause is the Terminologist's criterion, not the build seam.

## The measure on the walk

Attempts to a merge on the third request, from no merge in 8 attempts on
night 138 and 7 on night 139, to a merge within 4. The mechanism counts:
stored Tester tests that never run their criterion's path, from 3 of 4
and 3 of 3 to at most 1 in 3; Developer commits that fit a test the
session called wrong, from 2 of 3 on night 139 to at most 1 per night;
Architect answers to the Developer with no words, from 10 of 10 to at
most 1 in 3; challenges stamped answered with no reply, from 6 over three
batches to at most 1 per night. The residue rule as frame 193 wrote it: a
batch that still loops is read, and the frame closes when its cause is
not one the design named. Causes that are not this design's: the hidden
exception, frame 195; the reply cuts, frame 47; the span refusals, frames
173 and 140; the missing `tests_missing` wake, frame 182.
