# The seat as an exchange

Ruled 2026-09-12. The register measures one desk, one turn. The walks
measure the loop with a scripted principal that says yes and contests one
numbered line on one page. Nothing asserts across pages, and nothing
exercises the seat the way a person does. Night 21 showed a seat fault the
register cannot see: the same "Here is what I understand you want" page
put to the principal five times in a row, each one mechanically correct,
together tiresome.

## What is added

1. **The whole page, printed.** The driver prints each rendered page in
   full, in order, with the reply under it. A run reads as a chat log,
   and the agent judges it as a person would: ordering, repetition,
   wording, what each page asks.
2. **A turn-by-turn principal.** `probes/seat.py`: the run steps in the
   background, writes each page to a file, waits for the reply, lands it
   through `principal.land`, the door the TUI uses, and continues. No
   screen. Replies may be scripted ahead in `replies.txt`, one a line,
   so an exchange repeats.
3. **Strategic hesitation.** At each page the agent chooses a person's
   move: ask before approving; approve part of a page ("1 and 3 are fine,
   2 is wrong: ..."); change its mind at the touch note; reply with
   something unhelpful; repeat a sentence; let pages queue.
4. **Page-sequence cases.** Pin what that finds: a sentence, the pages it
   produces, the words on each, in order. The experience measured the way
   the desks are.

## What stays outside

Roman at the TUI with his own sentences is the final test, after click
merges cold.

## Findings

| date | run | what the exchange showed | what changed |
|---|---|---|---|
| 2026-09-12 | seat1, tipsI on the Titan, the agent at the seat | Page 1, confirm: the agent asked a question instead of saying ok ("equal share, or their own order?"). Page 2 came as the signoff page and never answered it. Page 2 listed the program's existing behaviour under "It would:", the same heading a plan gets; a person reads "It would: calculate the tip" as new work. Page 3, after "you did not answer my question", was the right page: the sentence's items, one "would not". A part-approval ("2 and 4 fine, 3 is wrong: ...") landed. Page 4, a clarify, asked an odd question back ("including the one who paid the tip?"). Page 5, a clarify, relayed a desk's internal question to the principal: "how does this relate to the area that has not been surveyed?" A person cannot answer that. Page 6, the touch note, read "the batch for s2 (...)" and predicted src/ paths the repository does not have; a contest on that line was accepted. Then the build, tests, and the fix loop. | findings to doors and briefs below |

Findings, in the order a person met them:

1. **A question at the confirm page is dropped.** The reply was a question;
   the next page was signoff with no answer. The landing session read a
   question beside no ruling as... nothing. Owed: a case (a question at
   confirm gets an answer page, then the confirm again).
2. **Observed behaviour under "It would:".** The page's heading is by
   item kind, not provenance. Mechanical: observed items render under
   "It does today:", decided ones under "It would:".
3. **An internal question reaches the principal.** "The area that has not
   been surveyed" is constraint zero's bookkeeping. The clarify door
   already refuses questions "about bookkeeping"; this one got through.
   Owed: the words that mark it, or the fact (a clarify whose refs are
   `@`-prefixed subjects only).
4. **The touch note leaks ids.** "the batch for s2 (...)" is a render
   fault: the page shows no ids by contract. Mechanical.
5. **The touch note predicts paths that do not exist.** src/split_bill.py
   on a repository with no src/. Judgement (the Architect), but the index
   knows the paths: a door can refuse a touch grain under a directory the
   index has never seen.

How seat1 ended: after page 6 the batch built, one test passed, four
were written, the fix loop ran four attempts on the tipsI signature
fork (one test wants `calculate_tip(total, people)`, another wants two
arguments; the Tester wrote both), the Developer was quarantined, and
the Titan sat in one generation for twenty-five minutes; stopped there.
Six pages, six replies, no merge. The whole log is
`plans/exchanges/seat1-tipsI-2026-09-12.md`.

| 2026-09-12 | seat2, click on the 3080, the agent at the seat | Page 2 showed click's existing behaviour under "It does today:" (finding 2's door). A question at that page ("is 2 to 5 something you will change?") landed as approve-all and was never answered. Page 3 carried nineteen reconcile findings, each "the README says X. The code shows X" in the same words; "approve 6 only, I am not reading nineteen of those" landed as approve for all twenty-five. Pages 4, 5 and 8 were clarifies that quoted the principal's own words back and asked what the question was. Page 6 asked a real question. Pages 7, 10 and 11 were agenda pages of seven restatements each, out of 81; "contest all seven" contested two observed items and the run asked the Vision Keeper to amend what the code does. Page 9 asked whether echo_json, approved twice, should proceed. Stopped at page 11, no build reached. Log: `plans/exchanges/seat2-click-2026-09-12.md`. | three doors (the hook's cap, the restatement door, the observed-item contest); the rest below |

Findings from seat2, continuing the numbering:

6. **A question at the signoff page lands as approve-all.** Twice. The
   landing case for it is attributed red on both 8B Liaison models.
7. **The principal's question comes back as a clarify quoting it.** Three
   times: the reply went to the owner, the owner answered, and the
   Liaison asked the principal what their question was. Owed a fact: a
   clarify whose text quotes the principal's own last reply.
8. **"Approve 6 only" approved everything.** A part-approval that names
   one line and dismisses the rest landed as approve for the rest.
   Judgement, the landing brief; a case is owed.
9. **The reconcile flood, seen from the seat.** 81 rows, seven a page,
   twelve pages; most restatements. The restatement door cuts the
   duplicates at the source. What a person said at page 10, "stop, no
   more README pages", has no ruling to land as: a ruling on a kind of
   page. For Roman.
10. **A contested finding contested the code.** Door landed.
11. **The item approved twice was asked about again.** The observed
    items' contested state (10) sent the run back through signoff.

Standing after the first exchange (same day): 2, 4 and 5 are doors
(b6be813, a8b0c0c, 48e7921). 1 is a register case,
`L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`,
recorded 0/5 on both Liaison models; a brief sentence for it turned a
green landing case red on each model and was reverted, so it stands
attributed. 3 is owed a fact: the clarify's refs.
