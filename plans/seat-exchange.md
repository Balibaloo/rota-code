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

Standing after the first exchange (same day): 2, 4 and 5 are doors
(b6be813, a8b0c0c, the touch-path door). 1 is a register case,
`L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question`,
owed its record. 3 is owed a fact: the clarify's refs.
