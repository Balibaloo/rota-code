# Frame 221, pass 1 review: the assert door (81f27127 over ee535945)

Rota workflow, the Vision Keeper's `problem.assert` door. Read-only review on the worktree `C:/Users/roman/rota_rv221`. Reviewer: Opus agent, 2026-10-14.

**Verdict: revise.** The challenge refusal works. The contest words check fails open on a drop and on a negation. The contest branch also admits a rewrite when the principal contested another line. `exhausted.md` still sends the seat into the refusal. High 3, low 4.

## (a) The verdict on each point

1. Wake signal: correct for challenge, exhausted and contested. A wake with no trigger message refuses only on `tick:exhausted` or a contested id.
2. Loop: yes. `exhausted.md` tells the seat to amend, and the door refuses that on a decided item. The route out is `msg.report_liaison`.
3. Words check: the door refuses s399, s128 and s312, and admits s329 and s413. The s399 refusal holds only by accident. A drop or a negation of the flag is admitted.
4. Candidate G: the door admits a new id on intake, consult and exhausted wakes. It refuses a new id on a challenge message only.
5. `challenge.md` matches the `decisions.author` door. No path shows the decision to the principal, so the decision stays unread.
6. STE: one pronoun for the principal and one passive in `contested.md`. 8 of 8 tests pass at HEAD. The parent reds and the budget line were not checked inside the cap. Three branches have no test.

## Point 1, the wake signal

`sandbox.py:708-711` builds `Ctx` with `wake_kind` and `wake_refs` from the wake. `runner.py:3301` sets `ctx.trigger` from `trigger_message`. A message wake gives its own id. A tick gives the first ref that resolves to a message, else None. The `exhausted` wake carries a batch id (`predicates.py:1009`), so its trigger is None, and the door keys on `wake_kind == "tick:exhausted"`. A `tick:contested` wake carries the item id, so its trigger is None, and the door keys on `id in wake_refs`. A challenge wake is a message with verb `challenge` (night 146: s354, m213). The relay branch reads `_principal_relay`. The VK `relay.tools` offers no `problem.assert`, so no VK relay session reaches that branch (reasoned: 9 modes offer `problem.assert`, and relay is not one of them). A wake with no trigger and any other kind returns None: probe p4 shows that `message:intake` and `tick:consult` admit an assert.

## Point 2, the exhausted wake

`exhausted.md` bullet 1 says "Amend it with `problem.assert` so it says what was actually meant". On a decided item the door now refuses that call. `exhausted.tools` offers `decisions.author` and `msg.report_liaison`, so the seat has a route. The correct route is `msg.report_liaison`. The ladder derives from committed `tick:exhausted` sessions (`predicates.py:1071-1088`). After the Vision Keeper, `_next_rung` returns an empty role, so nothing wakes again. A `decisions.author` alone leaves the batch exhausted with no page. The refusal text names `decisions.author` first, which leads the seat to the dead route.

## Point 3, the words check on night 146

Probe p3 used each session's own wake JSON for the old text and the words, as the implementer did. Results:

| session | result | right? |
|---|---|---|
| s399 | refused: `display`, `requiring` | Right outcome, wrong reason. The principal said "Ok, that is what I asked for" about line 1. The contest was on line 2. The item should not change at all. |
| s128 | refused: `using`, `cannot`, `include` | Right outcome, wrong reason. The words contest line 3 (a criterion) and line 5 (the tests of the batch). The seat folded criterion and batch content into the item. |
| s312 | refused: 6 words | Same shape as s128. The words name lines 1, 9 and 10. The content is the meaning of the principal in the words of the seat, on lines that are not the item. |
| s329 | admitted | Doubtful. The principal approved the item and asked to add to line 2. The seat added the words to line 1. |
| s413 | admitted | Admitted because the old text is the s399 rewrite, and the check counts the old text as carried. |

So s128 and s312 carry the meaning of the principal in the words of the seat, about criterion and batch lines. Variants on s399: a text that drops the flag with old words only is admitted. A text that says "will not include a `show_python` flag" is admitted. A retry of s128 in the words of the principal is admitted, so the item absorbs criterion and batch lines. The `contested.md` example lands (test `test_the_contested_briefs_own_example_lands`, green).

## Point 4, candidate G

`api.py:1239-1253` refuses an unknown id only when the trigger verb is `challenge`. Probe p4: a new id on `message:intake`, `tick:consult` and `tick:exhausted` returns None. A new id on trigger m213 (a challenge) is refused with the decision route. The refusal is narrow and correct.

## Point 5, the challenge route

`decisions_author` (`api.py:9060-9159`) admits a fresh id, `refs` to the item and no `supersedes`. The brief sentence matches the door. No principal page reads `decisions`. Its readers are `term_collision`, `_resolve_refs` and four sandbox checks. So the decision reaches a later seat only through refs, and the principal never sees it. A challenge that finds the words of the principal unworkable then ends with no question to the principal. That gap is a composition question, and the open question 3 of the implementer names it.

## Point 6, STE and the tests

- The refusal texts follow STE. They use no pronoun for the principal.
- `contested.md:18` reads "The new text carries their words. A text in your own words is refused." The first sentence uses a pronoun for the principal. The second sentence is passive. The file around the line uses "they" throughout.
- Tests: 8 passed at HEAD in 3.7s. The implementer reports s354, s399 and s328 red on the parent. This review did not re-run the parent inside the cap.
- Branches with no test: the exhausted refusal, the relay branch, the onboarding skip, and a contest with no words (admitted).
- This review did not check the budget line inside the cap.

## (b) Findings

1. `rota/roles/api.py:1300-1316`. High. CONFIRMED: probe p3 admits "The `version_option` appends the running Python version to the message." and a negated flag. The check reads only the words that the new text adds, so a drop or a "not" passes. Fix: refuse when a word of the old text that the words of the principal carry is absent from the new text, and count a negation word as new.
2. `rota/roles/api.py:1280-1287`. High. CONFIRMED: probe p3 admits s128 retried in the words of the principal. The contest flag turns on for any id in `wake_refs`, whatever the per-item verdict and whatever line the words name. Fix: set `contest` only when the verdict map rules this id `contest` or `revise`, and refuse when the words name only other lines.
3. `rota/roles/prompts/vision_keeper/exhausted.md:11-13`. High. CONFIRMED by reading: the brief tells the seat to amend, and the door refuses that call on a decided item. This repeats the frame 197 loop. Fix: add "An item with provenance `decided` is the principal's own words. Do not amend it. Send `msg.report_liaison` with what the item should say."
4. `rota/roles/api.py:1268-1272`. Low. PLAUSIBLE: the exhausted refusal names `decisions.author` first. A decision drains nothing, and no rung follows the Vision Keeper, so the batch stays exhausted with no page. Fix: name `msg.report_liaison` first, and say that it is the route to the principal.
5. `rota/roles/prompts/vision_keeper/challenge.md:6-10`. Low. CONFIRMED by reading: no reader shows a decision to the principal, so a challenge on a decided item never reaches the principal. Fix: escalate to Roman whether `challenge.tools` offers `msg.report_liaison`.
6. `rota/roles/prompts/vision_keeper/contested.md:18`. Low. CONFIRMED by reading: a pronoun for the principal and a passive. Fix: "The new text carries the principal's words. The door refuses a text in your own words."
7. `tests/rota/test_frame221_assert_words.py`. Low. CONFIRMED by reading: no test covers the exhausted refusal, the relay branch or the onboarding skip. The VK `relay` mode cannot reach the relay branch. Fix: add a test for the exhausted refusal, and remove the relay branch or name the mode that reaches it.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv221/`.

- `p3_words.py`: an in-memory copy of `D:/repos/rota/.rota/clickI_night146.db` (`mode=ro`). It runs `_assert_words_fault` from the worktree on s399, s128, s312, s329 and s413, with the old text and the words of each wake. It also runs three variants: drop the flag, negate the flag, and s128 in the words of the principal.
- `p4_newid.py`: a new id on `message:intake`, `tick:consult`, `tick:exhausted` and the challenge trigger m213.
- `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_frame221_assert_words.py -q` at HEAD: 8 passed.
- Inline reads of night 146: `tool_calls`, `sessions`, `turns`, `rulings`, `item_provenance`.

## (d) Usage

The context counter shows about 67k tokens in all: 14,979,326 at the start and about 14,912,000 at the end. The counter gives no split between input and output. The cap was 50k, and the review went over by about 17k.
