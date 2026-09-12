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
