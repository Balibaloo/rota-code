# Frame 204, pass 2: interview of the Developer on L1-DV-take-out-what-nobody-asked-for

Date: 2026-10-13. Workflow: the rota workflow (the Developer seat), read by
the meta workflow. Source: a sqlite backup of `tests/rota/cassettes.db` at
`scratchpad/itv204/cassettes.db`. Model `qwen3:8b`, temperature 0.0,
num_ctx 12288, think false. Replay script: `scratchpad/itv204/itv.py`.
Nothing was recorded.

## 1. The failing run

- Run seq 441145, run 1 of 5, `passed 0`. Problem verbatim: "none of the
  permitted answers was given; wrote [], sent [('vision_keeper',
  'question')]" (observed: case_runs seq 441145, 2026-10-13 06:33).
- Calls: `code.probe`, `criteria.load`, `msg.question_vision_keeper`.
  No `ledger.log` call. The seat asked before any log, so the door's
  `scope` refusal is not in the transcript (observed: case_runs seq 441145
  to 441149, all five runs the same shape).
- The turn's cassette is key `a7e2ca35d9d5983fce2aaac47e417a75`. Its
  completion: `msg.question_vision_keeper(refs=["c_560bd8"], question="Does
  the criterion require that a truncated string must end in an ellipsis
  character, or is it acceptable for it to end in other characters?")`
  (observed: cassette a7e2ca35).
- The mode is `challenge`. The brief's premise that the split is not in
  front of the seat is wrong. The system prompt carries `MODE: challenge`
  and the pass 2b split verbatim: "the item's words need the thing and do
  not name it: that is scope ... a criterion is silent, and you chose a
  reading of it: that is a default" (observed: cassette a7e2ca35 system).
- The wake names only the criterion `c_560bd8` "a truncated string ends in
  an ellipsis character". It carries no quote of the disputed span, no
  diff, and no item text. The rename `plural` to `pluralise` appears
  nowhere in the prompt (observed: cassette a7e2ca35 user). The case row
  gives the inbound `body_refs: [<c1>]` only
  (observed: `tests/rota/cases/l1_answers.yaml:253` at f7b8fc7e).
- The Critic brief tells a real challenge to carry "refs naming the
  criterion, quotes copying the span" (observed:
  `rota/roles/prompts/critic/review.md:47` at f7b8fc7e). So the case's wake
  is thinner than a real one (reasoned: the row omits `quotes`).

## 2. The interview, verbatim (observed: the interview, turn of cassette a7e2ca35)

1. "\"a truncated string ends in an ellipsis character\" made me ask the
   Vision Keeper, as it was unclear whether this was a requirement or a
   possible scenario."
2. "I understood \"scope\" to mean the boundaries of what the criterion
   applies to. Since the criterion was silent on whether other characters
   were acceptable, I needed to clarify if the ellipsis was a mandatory
   ending or just an example."
3. "... I did not know which part of the change Critic was disputing, but
   the reference to \"c_560bd8\" indicated it was related to the
   criterion's requirement for truncated strings."

No refusal told the seat to ask. The seat answered a question about the
only thing in front of it, the criterion (reasoned: answers 1 and 3).

## 3. Variant replays, one run each at temperature 0.0

The brief's variant is a no-op. No refusal is in the transcript, and the
split sentence is already in the mode's brief (reasoned: section 1). So the
variants test what the answers name instead.

| Variant | Change | Result (observed: the replay) |
|---|---|---|
| B | the diff of `formatting.py` with the rename added after `[criteria.load]` | asks VK: "Is the ellipsis character required for truncated strings in the formatting logic?" |
| C | `quotes` with the `pluralise` span added to the wake | asks VK: "Was the renaming of `plural` to `pluralise` requested, or was it an unasked-for tidy-up?" |
| D | C, plus the brief line "if that question is genuinely open, `msg.question_vision_keeper` is the route" replaced by "Read the item's words: if they do not need the thing, nobody asked for it. Take it out and commit. Ask the Vision Keeper only when the item's words need the thing and do not name it." | asks VK: "Does the function `pluralise` need to be present in the codebase according to the criteria?" |
| E | D's brief line alone, no quote | asks VK about the ellipsis criterion |

No variant wrote or committed. The quote moved the question to the right
thing (variant C), and nothing moved the action (observed: variants B to E).

Interview in variant D's context, verbatim (observed: the interview, turn
of variant D): "I asked because the function `pluralise` might be needed by
some item's words, which were not clear. The fact missing was whether the
function was required by any criteria or item."

## 4. Cause and fix line

Cause: the row's shape (reasoned: answers 3 and D). The wake does not name
the disputed thing, so the seat disputes the criterion. With the quote, the
seat still cannot read the item's words, because item `i1` "long subject
lines are truncated" is not in front of it. The brief then tells it that an
open question goes to the Vision Keeper, and the question is open to a seat
without the item. The door's offer is not the cause: no log was attempted.
The seat is not the cause: it asks honestly from what it sees.

Fix line for pass 2d (reasoned: untested, the next replay checks it):

1. Give the case's inbound a `quotes:` entry with the `pluralise` span, as
   the Critic brief requires of a real challenge. File:
   `tests/rota/cases/l1_answers.yaml` only.
2. Show the item's text beside the criterion in a `challenge` wake, for
   example a `[the item]` line: "long subject lines are truncated". File:
   the wake renderer for the Developer's `challenge` mode, which is in
   `rota/roles/api.py` or `rota/core/sandbox.py`. Both are edited by
   another frame now, so this step waits on that commit.
3. Replace in `developer/challenge.md` the line "if that question is
   genuinely open, `msg.question_vision_keeper` is the route" with: "Read
   the item's words. If they do not need the thing, nobody asked for it.
   Take it out and commit." This file is also edited by another frame now.

Replay variant D plus step 2 once before any edit. If the seat still asks,
the residue is the 8B seat on a first turn with no code read, and the case
can admit `msg.question_vision_keeper` on the quoted span as a third
honest answer (reasoned: the brief itself calls that route honest when the
question is open).

## Fallback (2026-10-13, two runs at temperature 0.0)

The item's text was added after `[criteria.load]` as a `[the item]` block:
`{"id": "i_3a91c2", "text": "long subject lines are truncated", "kind":
"in_scope", "approval": "approved"}`. The block shape is a stand-in, because
the wake renderer shows no item in a `challenge` wake today (reasoned:
section 1, the prompt has none).

| Run | Change | Result (observed: the replay) |
|---|---|---|
| F1 | variant D (quote and "take it out" brief line) plus the item | no write, no commit: `TOOL: msg.question_vision_keeper(refs, question, round_no=0)`, the signature copied with no values |
| F2 | the item alone, original brief, no quote | no write, no commit: asks VK "Does the criterion 'a truncated string ends in an ellipsis character' require that truncated strings end with an ellipsis, or is it sufficient for them to be truncated without specifying the ending character?" |

The seat's words on what decided the call, verbatim (observed: the
interview, turn after each run):

- F1: "The fact that the function `pluralise` was renamed from `plural`
  while passing, and the challenge suggests that nobody asked for this
  change, indicating it may be an unneeded addition."
- F2: "The fact that the criterion \"a truncated string ends in an ellipsis
  character\" was in scope and the item \"long subject lines are truncated\"
  was approved determined the need to clarify the criterion's requirement
  for an ellipsis ending."

The item's text is not the moving fact by itself (reasoned: F2 asks about
the criterion as before). In F1 the seat named the right cause and still
asked, so no wording in front of it moves the action on this first turn
(reasoned: F1 and variants B to E). The residue is the 8B seat: it asks
before it reads code.

Fix line now supported for pass 2d (reasoned: six replays, none writes):
give the case's inbound a `quotes:` entry with the `pluralise` span, and
add to `expect.any_of` a `msg.question_vision_keeper` answer as the third
honest route. File: `tests/rota/cases/l1_answers.yaml` only. Steps 2 and 3
of section 4 are withdrawn, because neither moved the seat.
