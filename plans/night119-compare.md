# Night 119: two blind reads, Opus 5.5 and Fable 5.1

Meta workflow. Roman asked on 2026-10-05 for a second read of night 119 on
Fable, beside the read on Opus, to compare the outputs. Both agents held
the same brief, word for word, and the same database,
`.rota/clickI_night119.db`. The Fable brief forbade the other file. The
reads are `plans/night119-read.md` (Opus) and
`plans/night119-read-fable.md` (Fable).

## Cost

| | Opus 5.5 | Fable 5.1 |
|---|---|---|
| Tokens on the harness line | 272.3k | 330.1k |
| Tool calls | 84 | 80 |
| Wall time | 13 min 52 s | 13 min 58 s |
| Lines in the record | 189 | 251 |

(observed: the two harness lines, 2026-10-05)

## The four verdicts

| Frame | Opus | Fable | The session's ruling |
|---|---|---|---|
| 120, the Developer's wake holds one traceback 34 times | closes, 7 of 7 | closes, 7 of 7 | closes |
| 123, a Tester's fix leaves two tests that contradict | closes, 0 of 1 | closes, 0 of 1 | closes |
| 125, the criteria door reads "already" as a name | closes, 0 turns | closes, 0 turns | closes |
| 122, a Critic's quote that holds quotes never parses | closes, with a caution on s229 | stays open, because of s229 | stays open |

The two reads agree on every number of frames 120, 123 and 125.

**Frame 122 is the one disagreement, and the Fable read is right**
(observed: `scratchpad/judge122.py` of session e6218d79 on the database,
2026-10-05). The Critic s229 sent `challenge.uphold` at turn 8 with
`why='... the parameter 'default_on_eof: bool = False' and ...'`. That is a
quote in a quote, on a function that keeps the third reading. The parser
answered `a quote inside citation ended it early and the arguments after it
(quote=...) were read as part of citation` three times. The seat moved two
quotes onto `quote`, the wrong argument, and the session ended at turn 12.
Both reads saw s229 and both named the cause. Opus applied the measure's
sign, which s229 does not show, and closed the frame. Fable applied the
residue rule, which reads the cause, and kept the frame open. The frame's
ends-when names the cause, so the frame stays open (reasoned: the residue
rule of 2026-10-03 closes a frame when the cause left is not the cause the
frame named, and here the cause is the same).

Both reads disagree on the count behind the measure, and both counts are
correct for their own definition. Opus counts sessions whose last refusal
is the sign after three turns or more: 1 of 291, s130. Fable counts
sessions with the sign in three prompts or more: 3 of 291, s246, s259 and
s260. All four are a Developer's `code.write`, which keeps the old reading
by design.

## The causes of the stuck things

- **The pause.** Both: the pause cut the Critic s188 only, and bg_1's park
  came before the pause.
- **bg_1, parked.** Both: s152 added `from .core import command`, a
  circular import, and no later commit removed the line. Fable alone names
  the origin: the cycle door told the seat to use that form, at s152's
  turn 5. Opus alone names the test that made s152 add `@command()`.
- **The given-up challenge.** The reads differ on who made the item. Opus:
  the Vision Keeper s165, frame 129's shape. Fable: the Vision Keeper s151
  in propose mode asserted a criterion's words first, and s165 then did
  frame 129's act on the same item. Not checked by this session.
- **bg_3, given up.** Both: `tst_v1` and `tst_v3` are wrong tests, the
  Tester s249 answered the challenge in prose and sent no encode, and s258
  then changed `version_option` and broke project tests. Opus counts 3
  broken tests in `tests/test_basic.py`. Fable names one, `inh_dcc9ea38`.
  Fable alone found that the door then refused every later challenge as
  answered, in 8 Developer sessions.

## New walls

Both reads hold five walls:

1. The swallow refusal names the first argument, and the stray quote
   stands in a later one: 13 refusals in 7 sessions. This is frame 122's
   residue, and it becomes that frame's next pass.
2. A test calls a plain function as a Click command, and the Developer
   changes the product to fit: 2 of 3 batches, both the stuck ones.
3. A Tester answers a challenge in prose and sends no encode: s249. Fable
   adds s271, 2 of 5, and the door that calls the challenge answered.
4. A Developer writes back the line that it says it removes: 0 removals on
   bg_1. Both ask for an interview first.
5. A large diff block removes the source from the fix wake: 6 of 20 wakes.

Fable alone holds five more. No one has checked these against the database
(reasoned: a finding of one read is a claim of one read):

6. The cycle door names a fix that is a cycle, s152 turn 5.
7. The fix wake's source is `src/click/testing.py::CliRunner`, not the file
   the traceback names, in 10 of 10 bg_1 wakes. Opus lists this as not
   determined.
8. A Developer's `code.write` never ends for three causes: `]` for `)`, a
   value with no closing quote, a looped reply. Opus holds the same three
   forms under frame 122 and does not call them a wall.
9. A Vision Keeper in propose mode asserts a criterion's words as an item,
   s151.
10. The returns-against-prints door refuses a test of an argument, 3
    refusals in s247.

Both reads found frame 130's cause in the other direction: 4 bg_3 wakes
show 34 passing project tests as red with bg_1's output.

## What the comparison says

- On counts against a stated measure, the two models agree. Every shared
  number is equal.
- On judgement, they differ once, and the difference decides a frame. Opus
  held the measure's letter. Fable held the frame's cause. This is one
  case, on one night.
- Fable found more: 11 walls against 5, one more session behind wall 3, and
  the origin of bg_1's break. Fable cost 21 % more tokens and the same
  wall time.
- This is the second count for the line "Opus builds, Fable judges". The
  first is frame 74's: Opus found 8 of 10 findings blind (observed:
  `plans/archive/stack-2026-09-23.md`, frame 74, 2026-09-24).
