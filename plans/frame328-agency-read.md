# Frame 328, the agency read: the encode note and the quote check

2026-10-26, at 46e5c88b, read-only. Registers 163 to 168 from a copy. Meta workflow.

## 1. The purpose

The encode run of `tests.encode` came from frame 304 at a3ce3f01 on
2026-10-23. It closed night 159's wall, a test red in its own arrange step
that no code can pass, and it admits a failed assertion on purpose (observed:
`_arrange_run_refusal`, `rota/roles/api.py` 17649; stack frame 304, judged
17:52). The quote check of `msg.challenge_tester` makes a challenge pay its
reading before it costs a Tester wake: "a contiguous span of the disputed row,
verbatim" (ruled: Roman, 2026-08-26, `rota/DECISIONS.md` 1248 to 1297). The
build 395535da of 2026-08-27 checked any 12 characters instead (observed:
`_quotes_span`, `rota/core/sandbox.py` 951).

## 2. What exists (observed: each file and line named)

| Record or code | Where | What it holds |
|---|---|---|
| `tests_missing` waits for `head_commit` | `rota/core/predicates.py` 790 to 845, 01e48a6f, 2026-09-08 | The Tester wakes only after a commit. Code first is the design |
| `tests_failing` | `predicates.py` 949 | Every red goes to the Developer only |
| Run output on a challenge wake | `rota/core/runner.py` 2985 to 3000, 3465 | The Tester sees its run only when challenged |
| `_encode_run`, `arrange_fault` | `api.py` 17378, 17649 | The run at encode. Passes 1 and 4 reuse it |
| `_own_assertions` | `api.py` 17447 | Notes an `AssertionError` in the test's file only |
| `_span_of`, `_seat_forms`, `_unescaped`, `_one_backslash` | `sandbox.py` 1246 to 1330 | Quote forms, one family per night: 119, 124, 126, 167, 167, 168 |
| `_call_keeps` | `api.py` 17530, frame 335 | Both parse paths of the call |
| `_quotes_span`, 12 characters | `sandbox.py` 983, 1216, 1222, 1710 | Still live |
| The contested-text block | `runner.py` 764, 7a2cb843, 2026-10-15 | Shows the Developer the old criterion text |
| Latest-run query | About 15 inline copies, e.g. `sandbox.py` 1195, 1573 | No shared helper. Pass 2 adds one more |

## 3. The reach

Mechanism 1, as the frame places it: a red test on a head that holds the
code is admitted, and its result does not reach the Tester. The provenance
read says no design covers this, because the charter puts the test first
(observed: `plans/frame328-provenance.md`). The code shows more. Since
01e48a6f the scheduler puts the code first on every batch, and no ruling or
doc records the change (observed: a grep of `DECISIONS.md`, `LAWS.md`,
`operating-facts.md`). So night 166 had the normal order, and the old premise
stands in these places (reasoned: the predicate and the records):

1. `_arrange_run_refusal` admits an own assertion with no note.
2. The same function is silent on a collection error.
3. The same function is silent on any other admitted red, because
   `_own_assertions` reads `AssertionError` only. First runs on nights 163 to
   168: 17 red, 8 own assertions, 6 collection errors, 3 other kinds
   (observed: `classify.py` in the reader's scratch).
4. `rota/roles/prompts/tester/base.md` line 3, "You write before the
   implementation exists".
5. `tester/tests_missing.md`, "There may be no code yet, and that is the
   normal case". The note tells the same seat "The batch's head holds the
   Developer's commit" (reasoned: cause 12, two records in one prompt).
6. `api.py` 9226, "written before the diff exists", and `rota/HANDOFF.md`
   176, "they were written first".

Mechanism 2: the quote predicate is wider than its fact. The window stands
on seven sites (observed: `plans/frame328-review-p1.md`, point 4):

7. Developer to Tester. 8. Critic to Tester. 9. Terminologist to Vision
   Keeper. 10. Architect to Vision Keeper. 11. Critic to Developer.
12. The Tester's answer, `_answer_evidence`, `sandbox.py` 983, on the same
   ruling. 13. The red-line door, `sandbox.py` 1216 and 1222.

Two signs beside the count. The strict side grew one escape reader per night
in six commits, each fitted to one sample (observed: the four docstrings).
The old text comes from the Developer's own prompt: on nights 166 and 168,
12 of 12 and 51 of 51 challenge calls ran in sessions shown "He contested
this text", and 18 of 65 challenge turns of night 168 held the old v1 words
(observed: the registers). The third clause went 5, 13, 7, not toward 0
(observed: `plans/night168-read.md` line 126). Count: 13 instances.

## 4. The fix against the reach

The fix covers 4 of 13 (observed: the diffs of 98c47ba2, 937b5093, 5ae7f5f5,
bde0e6ea, a9231619). Covered: 1 by the encode note, 2 by pass 4, 7 by the
strict check, 8 by the same branch, which keys on the recipient. Left: 3, the
other admitted reds; 4 to 6, the briefs and docs; 9 to 11, held by frame 333
and unbuilt; 12 and 13, named by review 1 and held by no frame. The
green-test refusal of 73c57a08 is sound, with one more inline query.

## 5. My proposal

Keep the encode note. Every Tester encode passes `_arrange_run_refusal`, so
that door is the source for mechanism 1's run. The rest moves:

1. One quote reader replaces `_quotes_span` on 983, 1216, 1222 and 1710;
   frame 333 takes sites 12 and 13 (observed: review 1, point 4).
2. The reader compares the quote with each view the seat was shown: the raw
   row, its JSON form, and the forms `_call_keeps` keeps (observed: `api.py`
   17530), not one decoder per night (reasoned: wall guide section 3).
3. The Tester briefs say the code exists and the run at encode is its first
   verdict, `base.md` line 3 and `tests_missing.md` (observed:
   `predicates.py` 790). Black-box stays. Measure on the register.
4. `_own_assertions` notes every red that `arrange_fault` admits after a
   Developer commit (observed: `api.py` 17447).
5. The contested block marks each old text as replaced and shows the live
   version beside it (observed: `runner.py` 764; night 168, 18 of 65).

Price (reasoned: `plans/operating-facts.md` 239 to 250). Lines 1 and 2: one
predicate pass, a review and a gate, 3 cycles, about 145k. Line 3: a brief
sentence that owes the register, 2 cycles, about 60k. Line 4: a door text,
2 cycles, about 60k. Line 5: shared runner prose, 2 cycles, about 70k. In
all, about 9 cycles, 335k on the agents' lines and 90k of the session.

## 6. The doubt

- The first-run counts are stored harness runs, not encode runs.
  `arrange_fault` can refuse the 3 other reds, and instance 3 then shrinks.
- 18 of 65 turns hold the old words, so the block is one source, not proven
  the only one.
- I did not read frame 304's design. A Tester-first ruling makes 4 to 6 right.

## Verdict

`at one door of 13`: the fix covers 4 of 13 (observed: sections 3 and 4).
Left: other reds at encode, three before-the-code records, three channels
on the window, the Tester's answer, the red-line door.
