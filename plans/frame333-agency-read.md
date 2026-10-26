# Frame 333, the agency read: one door of thirteen

Date: 2026-10-26 21:10. Read at 46e5c88b on `rota/foundation`. Read only. No
register was opened. Meta workflow.

**Verdict: `at one door of 13`. The frame's fix covers 3 of 13 instances.**
The cause is right: the quote check departs from the ruling of 2026-08-26. The
site is wrong: the three edges meet one block in `rota/core/sandbox.py`, not
three call sites in `rota/roles/api.py`. The same window guards two more doors,
and six texts plus one test depend on the window (observed: sections 2 and 3).

## 1. The purpose

The mechanism is the quote check of the verb `challenge` on every recipient
except `tester`: the tail of `_challenge_evidence`, `sandbox.py` 1700 to 1716,
through `_quotes_span`, 951 (observed). It closes the wall "challenging a test
costs less than fixing the code", where `L1-DV-fix-the-code-not-the-test` went
from 5/5 to 0/5 (observed: `DECISIONS.md` 1248 to 1282). e5be177e, 2026-08-19,
first asked for words of both rows on the Developer edge. Roman ruled on
2026-08-26, "why is this not obvious?", and the record says `challenge` carries
`quotes=` on all five channels and the binder refuses a paraphrase, "a
contiguous span of the disputed row, verbatim" (ruled: Roman, 2026-08-26,
`DECISIONS.md` 1290 to 1297). 395535da, 2026-08-27, built a 12-character
window, and named the non-tester form "the looser form of the rule" in a test
name only (observed: `tests/rota/test_challenge_evidence.py` 111). No record
holds that choice (observed: grep "looser" in `DECISIONS.md`, `LOOPS.md`, the
frame 328 records). So the window on these edges is an unrecorded build
decision of 2026-08-27 under a ruling that says otherwise (reasoned).

## 2. What exists

| Thing | Where | What it does |
|---|---|---|
| `_span_of` | `sandbox.py` 1246 | The quote is a contiguous span of the source, floor 12 or the whole row, three call forms. |
| `QUOTE_MIN` | `sandbox.py` 1237 | The floor, 12. |
| `_quote_list` | `sandbox.py` 1368 | The quotes as a list, from the binder or split from stored text. |
| `_quote_refusal` | `sandbox.py` 1385 | The refusal per row, with the short and the both forms. |
| `_seat_forms`, `_one_backslash`, `_unescaped` | `sandbox.py` 1288, 1325, 1339 | The seat's call syntax and escape forms. Tester edge only today. |
| `_cites` | `sandbox.py` 1663 | The per-side check. A closure in the tester branch, not a helper. |
| `_QUOTABLE` | `sandbox.py` 934 | Six tables. `statements` is not one. |
| `_quotes_span` | `sandbox.py` 951 | The window. Callers 983, 1216, 1222, 1710. |
| the binder | `sandbox.py` 3743, 4690 to 4724 | Hands every channel the quote list as `spans`. |
| `.tools` lists | `prompts/*/*.tools` | Five edges: Developer and Critic to Tester, Critic to Developer, Architect and Terminologist to Vision Keeper. |

(observed: the file at 46e5c88b). The helper the frame names exists as
`_span_of` and `_quote_list`. The Tester edge's own rule is inline (reasoned).

## 3. The reach

The gap: a check that a record or a design calls a verbatim quote is the
12-character window, or the rows it should read are not read. Instances:

| # | Place | Gap | Origin |
|---|---|---|---|
| 1 | `sandbox.py` 1710 | Terminologist to Vision Keeper on the window | 395535da, ruling of 2026-08-26 |
| 2 | `sandbox.py` 1710 | Architect to Vision Keeper on the window | same |
| 3 | `sandbox.py` 1710 | Critic to Developer on the window | same |
| 4 | `sandbox.py` 934 | `statements` not quotable, so 121 of 229 Architect challenges are unchecked, and `deliver.md` 9 to 10 asks "the exact span of each" while the door asks one | review 1, point 4 |
| 5 | `sandbox.py` 983 | `_answer_evidence`: "a verbatim span of a criterion" on the window | e3cbfbb0, Roman's call 2026-09-15 |
| 6 | `sandbox.py` 1216, 1222 | `_red_line_refusal`: "the quote holds that line" on the window, every channel | 1055a2c5, frame 213, 2026-10-13 |
| 7 | `terminologist/criteria.md` 36 | Challenge "with the ticket", no `quotes=` | brief |
| 8 | `terminologist/criterion_repair.md` 44 to 45 | "send `msg.challenge_vision_keeper`", no `quotes=` | brief |
| 9 to 12 | `api.py` 6005, 6080, 6847, 6970 | Four refusals offer the Vision Keeper challenge with no quote | frame 135's law: a hint names a call every door admits |
| 13 | `test_challenge_evidence.py` 111 to 121 | Pins a quote plus commentary as admitted | 395535da |

Count: 13 (observed: each line read; the 121 of 229 from
`plans/frame328-review-p1.md` 61 to 69). Instance 6 sits under a build design
and no ruling of Roman's (reasoned). Without it the count is 12 and the
verdict holds. Review 1 measured 182 of 206 Terminologist challenges that the
strict check refuses, because the text is a proposed wording (observed:
`frame328-review-p1.md` 63, 69). Instances 7 to 12 are why (reasoned).

## 4. The fix against the reach

The fix is proposed only. Its Ends-when covers 1 to 3 (observed: the frame
block). Instance 13 goes red under it and the implementer must change it
(reasoned). It leaves 4, 5, 6 and 7 to 12. Its clause "the 12-character window
is gone from the file" cannot hold in `api.py`, which holds no window, and in
`sandbox.py` it holds only if 5 and 6 move too (observed: callers of
`_quotes_span`). Built as written, the strict door meets briefs and hints that
send no quote. That is a new wall of the 182-of-206 shape on the Terminologist
edge, cause 9 by `wall-guide.md` section 4, step 4 (reasoned).

## 5. The proposal

Not the same fix. Mine, at `_challenge_evidence` and its two sibling doors:

1. Replace the tail at `sandbox.py` 1710 with a per-quote rule: each quote of `_quote_list` is a `_span_of` of a quotable row in refs, and each such row has a quote (ruled: `DECISIONS.md` 1294, "on all five of its channels").
2. Add `("statements", "text")` to `_QUOTABLE`, `sandbox.py` 934, so the Architect's "exact span of each" is checked (observed: `deliver.md` 9 to 10; review 1, 121 of 229).
3. Move `_answer_evidence`, 983, to `_span_of` per quote, and `_red_line_refusal`, 1216 and 1222, to "the normalised line is inside the quote". Then delete `_quotes_span` (ruled: Roman, 2026-09-15, e3cbfbb0; observed: the docstring at 1179).
4. Add "`quotes=` copying the words you dispute" to `criteria.md` 36, `criterion_repair.md` 45 and the refusals at `api.py` 6005, 6080, 6847 and 6970 (reasoned: frame 135's law; review 1, 182 of 206).
5. Rewrite the pin at `test_challenge_evidence.py` 111 to the strict form. Pin one refusal per edge, and replay one Terminologist challenge turn before the night (observed: the Ends-when's red tests; reasoned: cause 5 replay rule).

Price, from `plans/operating-facts.md` 239 to 247: 1 implementer pass cold,
74k to 77k by anchor and 100k to 230k by frame 328's passes; 1 review, 69k to
76k; 1 gate with re-records, about 6k in the session. The brief lines make the
Terminologist and Architect cases stale, about 16 cases by the count for
the same change on 2026-08-19 (observed: the e5be177e message). That is 3 to 4 cycles, about 30k to 40k of
the holding session at 10k a cycle, against the frame's 1 cycle and a review.

## 6. The doubt

- The 182 of 206 and 121 of 229 counts are review 1's probe on end-state rows. I opened no register and ran no strict check myself.
- I did not read the cassettes, frame 285's decision-step offer, the answer-mode offers at 1042, or whether a `statements` id can collide with an earlier `_QUOTABLE` table.
- Instance 6 is a build design, not a ruling. If Roman reads the window there as the right form, the count is 12 and the proposal drops its half of line 3.

## Verdict

`at one door of 13`: the fix covers 3 of 13 (instances 1 to 3). It leaves the
statement row (4), the Tester's answer (5), the red-line door (6), two brief
lines (7, 8), four refusal texts (9 to 12) and the pinning test (13), which
goes red by force.
