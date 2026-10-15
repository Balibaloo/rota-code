# Frame 243, review 2: the contest block on the Terminologist's relay wake (cc6cbf57)

Reviewer: read-only diff review on Opus, worktree C:/Users/roman/rota_r243b at cc6cbf57, 2026-10-15. Meta workflow.

**Verdict: accept with one fix before night 150.** The block reaches s190's wake with his words whole, after the relay message, and the test is red at the parent for the right reason. One high defect: the block also shows on relays where the principal approved the criterion. On night 149, four relays on cr_5 carried his approve and would now show two old contests under "the principal contested these criteria".

## (a) Verdicts on the six points

1. Rebuild: CONFIRMED. At cc6cbf57 the s190 wake shows the block after the relay message, 12 entries, 7,454 characters. The parent shows no block.
2. Reach: the Terminologist's relay only, but on any relay whose criteria hold a past contest, not only a contest relay. A relay with no contest on its criteria stays byte for byte as before.
3. Size: the wake keeps its end on night 149 (reasoned estimate, about 8k to 9k tokens of 16,384). A grouped form loses no fact and saves about 4,100 characters.
4. criterion_repair: yes, a route. s178 held his words six times without the contested text, and wrote "instead of raising UsageError" back into cr_2, cr_4 and cr_6. The block there costs about 3,700 characters, the same size as the present lines.
5. Test: red at the parent on the block assert, green at HEAD, 14 passed, 0 CR. The re-recorded case gives the same sense 5 of 5, but its block shows the fixture placeholder "seeded verdict", so the case does not measure the block.
6. Night 150 line: see the end of the answers.

## Answers

### 1. The s190 wake, rebuilt

- The probe copied clickI_night149.db, opened ?mode=ro, through the sqlite backup API into the scratchpad. It deleted the rulings with rowid above 20, so the two rulings that had landed at s190 remain: r_3aa5b4358e and r_cb56c527ea.
- It built the prompt through rota.core.runner.build_prompt, as the test does: Wake("terminologist", "message", message_id="m88", detail="relay"), resolve_inbound, push_working_set.
- HEAD: "The message that woke you:" at index 57, the block header at 3,073, "Already run for you" at 10,570. The block holds 12 entries, cr_1 to cr_6 each with r_3aa5b4358e then r_cb56c527ea, each with "He contested this text:" then "He said:".
- Parent: the same build with _relay_contest_block replaced by an empty return, which is the whole diff in build_prompt. No block header. 0 CR in the output.
- The rebuilt parent prompt differs from the recorded s190 prompt in two ways only: the criteria texts (the copy holds the end-of-night texts) and the code.callables push (the copy has no project root). Neither touches the block.

### 2. Which wakes get the block

- The guard is role == "terminologist" and inbound verb == "relay" (runner.py:511). The mode does not count, so a park relay in criterion_repair mode gets it too. No other role gets it on a relay.
- The rows are the relay refs that are criteria. The block lists every non-stale contest ruling on each, from contests_on, whatever the relay says now.
- No contest: on night 149, the relays m10, m47 and m60 build an empty block, so no line is appended. The test test_a_terminologist_relay_with_no_contest_shows_no_block holds the same. Byte for byte as before.
- A relay with an approve on a criterion that he contested before gets the block. That is finding 1.

### 3. Size and the window

- Night 149, block per relay at its time: m77 6 entries 3,731 characters; m88 12 entries 7,454; m108 9 entries 5,607; m122, m123, m133, m134 2 entries 1,224 each.
- s190 recorded turns: system 6,988 characters, user 11,730 on turn 1 and 16,483 on turn 3, num_ctx 16,384, qwen3.5:9b. With the block, turn 3 is about 30,900 characters, about 8k to 9k tokens at 3.5 to 4 characters a token. The window holds, and Ollama cuts from the front only past the window (reasoned, no tokenizer run).
- Repetition: 2 distinct "He said" lines, 419 and 399 characters, each 6 times, 4,908 characters. The current ruling words also stand whole in principal_said, so the prompt holds them 7 times.
- Grouped form, one ruling heading, the words once, each criterion with its contested text: every fact stays, because the contested text is per criterion and the words are per ruling. The words fall to 818 characters, and the block to about 3,400.
- One fact is absent in both forms: his words cite page lines ("Lines 2, 3, 5 and 7"), and the block names no line. That is finding 3.

### 4. The tick:criterion_repair wake

- _last_word_lines (runner.py:410-444) gives, per criterion of the Tester question, the last ruling words when its verdict is contest or revise, and "Do not send the sentence he contested." It shows neither that sentence nor an earlier ruling.
- Night 149's s178 was this wake, on m78, after r_3aa5b4358e. The rebuild at HEAD shows 12 lines, 3,600 characters, the words six times, no block, no contested text.
- s178 was the last writer of the criteria before s190 (tool_calls: s163, s173, s178, s190 only). The texts at s190 carry "instead of raising UsageError" in cr_2, cr_4 and cr_6. So the declined words survived a wake that held his words six times.
- As a candidate: _contest_block on the question criteria costs about 3,700 characters at s178, the same as the present lines. It adds the contested text and the earlier rulings. It is a frame of its own, because the cases for that wake are different.

### 5. The test and the re-recorded case

- At HEAD: tests/rota/test_pushes.py, 14 passed.
- At the parent (an autouse fixture that sets _relay_contest_block to an empty return): the night 149 test fails on "assert head in user", the block header. The no-contest test passes, as a guard should.
- git show cc6cbf57 holds 0 CR.
- The case L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told: runs at 2026-10-15T17:58 and at 2026-10-13T21:06, 5 of 5 passed each. Every run writes the same sense: return the default at once and never read stdin again. Two new runs add a second respecify that fixes surface_refs. The sense did not change.
- The recorded prompt shows "c_59d59b, ruling r_m_rule_c4308c: He said: seeded verdict". The fixture writes that placeholder (rota/testkit/fixtures.py:115-117), and the real words stand in principal_said. That is finding 6.

### 6. One line for night 150's read

On each Terminologist relay wake, count the block only where principal_verdict says contest, and count respecify texts that keep a contested phrase. Baseline night 149: s178 kept "UsageError" in 3 of 6 rows, and s190 wrote it back twice.

## (b) Findings

1. **rota/core/runner.py:511-516, high, CONFIRMED.** The block shows on a relay where he approved the criterion. On night 149, m122, m123, m133 and m134 relay cr_5, and each principal_verdict gives cr_5_confirm_default_on_eof the verdict approve. Each would show r_3aa5b4358e and r_cb56c527ea under "the principal contested these criteria". m133 says "Change the implementation, not the line". The block then invites a rewrite of a criterion he kept. contests_on also ignores a later approve, such as r_80d30c50e6 on cr_3, cr_5 and cr_6. Fix: keep a ref only when the inbound principal_verdict for it is contest, and add night 149's m133 as a no-block test.
2. **rota/core/runner.py:489-498, low, CONFIRMED.** On s190 the block repeats each ruling's words once per criterion: 12 entries, 7,454 characters, and the current words 7 times with principal_said. Fix: group by ruling, with the words once and each criterion's contested text under them.
3. **rota/core/runner.py:489-498, low, CONFIRMED absence, PLAUSIBLE impact.** His words cite page lines, and the block names no line. On night 149, line 1 is the item, lines 2 to 7 are cr_1 to cr_6, line 8 is bg_2, and the contested texts agree. Fix: in the grouped form, give each criterion its page line, after a check that per_item order is page order.
4. **rota/core/runner.py:501-510 and the commit body, low, CONFIRMED.** The docstring says s190 read "the relay's paraphrase alone". The recorded s190 prompt held the words of r_cb56c527ea whole in principal_said. The new facts are the first ruling's words and the contested texts. Fix: say in the docstring what the block adds, so night 150's read tests the right cause.
5. **rota/core/runner.py:410-444, low, CONFIRMED.** The tick:criterion_repair wake shows the last ruling's words only, without the contested text. s178 held them six times and kept "UsageError" in 3 of 6 rows. Fix: push a frame that gives that wake _contest_block in place of _last_word_lines.
6. **Outside: rota/testkit/fixtures.py:115-117, low, CONFIRMED.** The fixture seeds rulings.words as "seeded verdict". The re-recorded case now shows "He said: seeded verdict" beside the real entry in principal_said. The 5 of 5 green shows that the block does not break the case. It does not show that his words move the seat. Fix: seed words from the config value entry:<message id> when present.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cd6300cd-93cb-43d0-81c1-5833e2698637/scratchpad.

- p1.py: listed the night 149 rulings, m88, the s190 session row and the Terminologist messages, read-only.
- p2.py: copied night 149 by the backup API to n149_s190.db and deleted the rulings with rowid above 20.
- p3.py: built the s190 prompt at HEAD and with the block off. It wrote userH.txt, userP.txt and userRec.txt, and checked the order and CR.
- p4.py: measured the s190 turns and the block entries and repetition.
- p5.py: the block per Terminologist relay at its own time, and the Terminologist sessions.
- p6.py, p7.py: resolved m122 and m133. Each principal_verdict is approve on cr_5.
- p8.py, p9.py, p10.py: read tests/rota/cassettes.db read-only. They listed the case runs at the last two hashes and the recorded prompt.
- p11.py: rebuilt the s178 criterion_repair wake at HEAD and listed its respecify calls.
- parentpatch.py: a pytest plugin that turns the block off. It ran the two new tests: 1 failed, 1 passed.
- pytest tests/rota/test_pushes.py at HEAD: 14 passed.
- No gate run. No point needed it.

## (d) Usage

About 75k input tokens and 12k output tokens, about 87k in total, by the reviewer's estimate. The harness line is the measure.
