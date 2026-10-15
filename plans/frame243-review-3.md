# Frame 243, review 3: pass 2b at 966a978f

Reviewer: a read-only Opus agent, 2026-10-15 18:58, on a worktree at 966a978f. Meta workflow.

**Verdict: accept, with two lows for night 150 and one low to push.** Review 2's high is fixed on the relay wake. Night 149's four approve relays show no block, and s190's relay keeps the block whole. The grouped form keeps every ruling's words and every contested text once, oldest first, in less than half the characters. The criterion-repair wake now holds the last ruling's words seven times on s178. That is the repetition that review 2's finding 2 removed from the relay. The builders' block still shows old contests on a criterion that he approved later.

## (a) The six points

1. Fixed (CONFIRMED). m122, m123, m133 and m134 each carry `principal_verdict == {cr_5: approve}` and get a block of 0 characters. s190's relay m88 gets a block of 3518 characters, with both rulings whole. m108 gets 3405 characters with three rulings.
2. Holds (CONFIRMED). On m77, m88 and m108, each ruling's words occur once and each contested text occurs once. The rulings show in rowid order 19, 20, 23. The size goes from 3731 to 1713 characters on m77, from 7454 to 3518 on m88, and from 5607 to 3405 on m108. Pass 2's 7454 on m88 is the number review 2 measured, so the rebuild is faithful.
3. The block is present and correct, but the wake now repeats the fact (CONFIRMED). On s178 at m78's time, the old lines give r_3aa5b4358e's words 6 times, and the block gives them a 7th time. The old lines are 3613 characters and the block is 1714. The old lines should shrink. Finding 1.
4. No, a relay with `revise` gets no block. The repair wake treats `revise` as a contest, but its block drops a revise ruling. The try record counts 10 revise rulings on criteria in 66 nights, so the gap is a low. `contested_texts` already stamps texts for `revise`, so the fix is one predicate. Finding 2.
5. Holds (CONFIRMED). Against pass 2's runner at cc6cbf57, the 966a978f test file gives 6 failed and 11 passed. The 3 new tests fail on their own assertions: a block on the approve relay, `assert 6 == 1` on the words count, and no block on the repair wake. The 3 moved tests fail on the old per-criterion form. At 966a978f the pass report shows 36 passed. The moved relay test checks more than before: the heading, the criterion list, each text in order, the words and the ruling order. The removed check, 12 per-criterion headings in criterion order, has no subject in the grouped form. CR bytes: 0 in both files.
6. Night 150's line: count the Terminologist relays and repair wakes with the block, check that each approve relay has none, and count the respecified criteria that keep a contested text, against night 149's 3 of 6 "UsageError" rows on s178.

## (b) Findings

1. **rota/core/runner.py:432-452, low, CONFIRMED.** The repair wake gives each contested criterion its "last word" lines and then the grouped block. On s178, the words of r_3aa5b4358e occur 7 times and "Do not send the sentence he contested." occurs 6 times. Review 2 measured the same 7 on s190 and called it finding 2. Fix: when the block is present, keep one instruction line and drop the per-criterion words, or group the old lines by ruling.
2. **rota/core/runner.py:476-479 and 538-541, low, CONFIRMED in code, PLAUSIBLE in impact.** `contests_on` keeps `contest` only, and `_relay_contest_block` keeps `contest` only. The repair wake adds a ref when its last ruling is `revise` (runner.py:437), and that ref then shows no text in the block. `rota/roles/principal.py:717` stamps `texts` for `revise` too. Night 149 has one revise on a criterion id, r_196d6b58dc on `confirm_default_on_eof`. Fix: accept `revise` in `contests_on` and in the relay predicate, or record why the block excludes it.
3. **Outside: rota/core/runner.py:465-486, used at runner.py:2974, low, CONFIRMED.** The builders' block still shows a contest after a later approve. On night 149 at m134, cr_3, cr_5 and cr_6 are approved last, and the block on them is 2136 characters of old contests. This is the second half of review 2's finding 1, and the try record counts 38 such criteria. Fix: in `contests_on`, keep only the contests after the criterion's last approve.
4. **Outside: tests/rota/test_pushes.py:413-415, low, CONFIRMED.** The moved test's docstring still says that s190 respecified "from the relay's paraphrase". Review 2's finding 4 corrected the runner's docstring and left this one. Fix: say that s190 held his words in `principal_said` and no contested text.

Not found: no CR, no dropped check, no wrong order, no block on a non-criterion ref (m60 contests the glossary term `echo_json_helper` and gets none).

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/cd6300cd-93cb-43d0-81c1-5833e2698637/scratchpad/r243c/`. Each opened `D:/repos/rota/.rota/clickI_night149.db` with `?mode=ro` and copied it by the backup API.

- q1.py: listed the 10 Terminologist relays, cut each copy to the rulings whose reply came before the relay, and ran `resolve_inbound` and `_relay_contest_block` at 966a978f.
- q2.py: built pass 2's per-criterion block and pass 2b's block on m77, m88 and m108. It counted words, texts and order, and wrote `m88_new.txt`.
- q3.py and an inline probe: rebuilt s178's `tick:criterion_repair` wake on m78, cut at m78's seq, and counted the words. It wrote `s178_wake.txt`.
- An inline probe: listed `contests_on` and `last_ruling_on` for cr_1 to cr_6 at m134, and the revise rulings.
- pytest: `t/test_pushes_new.py`, a copy of 966a978f's test file, ran from a second worktree at cc6cbf57 with `-p tests.rota.conftest`: 6 failed, 11 passed. A first run without the plugin imported 966a978f's code and passed 17. That run proves nothing.
- No gate run. No point needed it. Both worktrees are removed.

## (d) Usage

About 45k input tokens and 9k output tokens, about 54k in total, by the reviewer's estimate. The harness line is the measure.
