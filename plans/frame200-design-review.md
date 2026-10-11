# Frame 200 design review, Opus, 2026-10-11 06:23

The reviewer's report, verbatim from its final message. The harness
blocked its write to the scratchpad, so this file is the only copy.
187.6k on the harness line against 100k. Probes under the session's
scratchpad `rv200d/`: `p1.py`, `test_right_meta.py`, `n138p5.db`,
`n139p5.db`. HEAD cad3e051. Rota workflow.

Verdicts: 1 CONFIRMED, 2 CONFIRMED, 3 PLAUSIBLE, 4 CONFIRMED, 5 CONFIRMED,
6 PLAUSIBLE, 7 PLAUSIBLE. Do not start as written. Change 5 matters most.
As written, it marks every right Tester re-encode and every Vision Keeper
decision unresolved, and wakes the Architect or the Liaison for them.
Pass 1 can start once the fixes to changes 1 and 2 are in the design.

## 1. Change 1 admits every right test

CONFIRMED. The design text has two gaps that the scope's section 7 does not have.
- **The call form is not covered.** The design says "a local `def` with no `command` or `group` above it", which only covers the `@` form.
  - All 11 Tester bodies of night 139, so 3 of 3 stored tests, use the call form: `version_option(...)(cmd)` then `decorated()`, or `custom_version_option(cmd, ...)` then `decorated()`.
  - A check that reads only the decorator lines refuses 0 of them (observed: `p1.py`).
  - On night 138 the `@` form catches only s379's v13. The v14 body (s381) has `@click.command()` and no `--version`, so no form of change 1 refuses it.
- **The design drops the scope's limit "factories that add an option".** `make_pass_decorator` and `pass_meta_key` pass `_returns_factory` and add no option.
  - `test_right_meta.py` decorates a local function with `@pass_meta_key("v")` and calls it inside `with ctx:`. The test passes on clickI.
  - The design text refuses that test, and the scope's limit admits it (observed: pytest 1 passed, and the model of change 1).
- `pass_context` stays admitted, because `_returns_factory` is False for it. The door reads only names in `surface_now`.
- No recorded body is refused: 0 of 537 Tester cassette bodies and 0 of 25 clickI test files.
- `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` has no factory in its tree, so its replay cannot meet the refusal. The scope's risk line on that case is wrong.
- Fix:
  - Name both the `@` form and the call form `f(...)(local_def)`.
  - Also name a factory's return that is called with no function argument.
  - Keep "that adds an option". Read it as a factory whose return or inner decorator is `option(...)`, `argument(...)` or `_param_memo`.
  - Refuse `.invoke` only on a runner receiver, as `_plain_invoked` does.

## 2. Change 2's two refusals and the empty-commit note

CONFIRMED. After a challenge lands, two existing refusals still tell the seat to change the code. Change 2's write door then refuses that change.
- The two refusals:
  - `_waits_refusal` (`sandbox.py:1236-1246`) says "write the change that makes it pass".
  - `_code_step` (`sandbox.py:1299-1312`) says "Make one real change to the code the test calls."
- The same-refs door runs at `sandbox.py:2218`, before the duplicate guard at 2760. Two doors that contradict each other are frame 194's class.
- After change 2, the note still says "with no message to anybody" to a session that has sent a message.
- Replays: in 0 of 10 cases whose latest runs contain `msg.challenge_tester` does `code.write` or `code.commit` follow it. Both cases the design names are among the 10. So pass 1 moves 0 records, and the design's "may change" can go.
- The end-of-work line at `runner.py:4127-4130` still follows every sent message.
- Cost of a right fix after a right challenge: one Developer session. It can also cost one attempt of `loop_cap` 10, because the Tester's re-encode runs the harness.
- Fix: when `_sent_this_session(ctx, "tester", "challenge")` holds, `_code_step` and `_waits_refusal` give `END_STEP`. The note then says only "you have sent your message: end the session".

## 3. Change 3 against `answer.md:25-27`

PLAUSIBLE. The branch asks nobody, so it stays inside lines 25-27. It can still end a wake that owes a write.
- `L1-DV-apply-the-answer-and-carry-on` is itself a wordless answer: refs only, no test, and it expects `code.write` and `code.commit`. It guards the first condition of the branch.
- No case guards a right red test with a wordless answer.
- After change 4, an Architect answer shows a decision row's text. The design does not say whether that text counts as words.
- With O3b held, the next `tests_failing` wake can meet "Make one real change to the code the test calls". The fit then moves one wake later and does not stop.
- Fix:
  - Fire the branch only when the session challenged or escalated about this test.
  - Add a guard case: a wordless answer with a right red test, expecting `code.write` and `code.commit`.

## 4. Change 4 against law 2 and frame 115's history

CONFIRMED. The row route stays inside law 2, "reached by following a ref" (`rota/LAWS.md:112-116`). Frame 115's status of 2026-10-04 14:38 records it as a build frame that needs no ruling. Two defects remain.
- **Wrong site.** `_resolve_refs` is in `rota/core/runner.py:2012-2113`, not in `sandbox.py`.
- **The row about a test reaches no seat that can change the test.**
  - `graph.json` has no `architect -> tester` edge.
  - The Developer's answer mode has no challenge tool, and change 3 ends that session.
  - The next challenge can meet the per-criterion cap `LANDED_CHALLENGES`.
- The row itself needs no ruling. A route to the Tester needs one: O4b, or a new edge.
- Fix: before the night, say how the row reaches the Tester. The cheapest route is a challenge that carries the row's ref, because `_resolve_refs` treats every role the same. That challenge must not count against the cap when its refs add a decision row. Otherwise, get the O4b ruling now.

## 5. Change 5's loop

CONFIRMED. The `unresolved` tick has no once-guard, and change 5 as written marks designed replies unresolved.
- **The bound.** `predicates.unresolved` skips a role that has spoken in the thread. After that, the only bound is `tick_attempt_cap` 3 on one tick key. A woken role that writes a row and sends nothing has not spoken, so it can be woken on the same row up to 3 times.
- **Tester replies.** `tester/challenge.md:14` says a right challenge gets `tests.encode`, not an answer.
  - On the two nights, 8 Tester sessions replied that way.
  - With those 8 rows set to unresolved, the predicate wakes the Architect's `tick:unresolved` 8 of 8 times (observed: `n138p5.db`, `n139p5.db`).
- **Vision Keeper replies.** The scope's 6 rows "stamped answered with no reply" are all challenges to the Vision Keeper.
  - `vision_keeper/challenge.md` says "author a decision saying why".
  - The graph gives the Vision Keeper no answer edge to the Architect or the Terminologist.
  - Set to unresolved, 4 of the 6 wake the Liaison, which puts them on the principal's page. The other 2 sit with no wake.
- **The note.** The design gives no text, and `COALESCE` keeps the first note.
- Fix:
  - Limit change 5 to a session that sent nothing caused by the trigger and wrote no receipt on a row the trigger refs. A decision row that cites the trigger counts as a receipt.
  - Give the note's exact text.
  - Re-count frame 174's baseline with this definition.

## 6. The measure

PLAUSIBLE. Two of the four counts are queries on the night's database. The other two need a read.
- **Wordless Architect answers: a query.** In `messages`: from architect, to developer, verb answer, empty `body_text`. After change 4, add: no `decisions` id in `body_refs` beyond the cause's refs.
- **Challenges with no reply: a query.** Rows in `messages` with no row whose `cause_id` is the challenge. It needs the definition from point 5, or designed replies are counted.
- **Commits after the same session's challenge: a query plus a read.**
  - `tool_calls.seq` gives the order, and `receipts` on `batches` shows the commit.
  - `messages` has no session column, so a challenge is matched to its session by role, refs and order.
  - The answer-mode half (s282) needs a read of the turn.
- **Stored tests that never run the path: a read.**
  - `tests` keeps the last body only. Earlier versions exist only in `turns`.
  - After change 1, every stored body passes the predicate by construction. So a script cannot count the shapes the predicate misses, such as v14.
- Fix: write the four queries into the design. Name the test count as a read of the stored versions in `turns`.

## 7. The order of the passes

PLAUSIBLE. A night on pass 1 alone does not measure the frame. Its loop would hit frame 115's wall, the wordless answers, and the ruling of 2026-10-09 20:19 stops a night like that.
- Pass 1 moves two of the four counts. A Developer that cannot write after its challenge escalates instead, and the escalation gets a wordless answer until pass 2.
- Dependencies:
  - Change 3's word "words" depends on how change 4 shows a decision row.
  - Change 2 needs the two refusal texts from point 2.
  - Change 5 needs the definition from point 5 first.
  - Change 1 is independent.
- Frame 202, where c1's text and its surface ref name different functions, is still a cause on night 139's batch. The walk's third request must avoid that batch, or the residue rule must name frame 202.
- Fix:
  - Keep one night at the end.
  - Move the `_code_step` and `_waits_refusal` lines into pass 1.
  - Do change 5 first in pass 2, after its definition is fixed.
