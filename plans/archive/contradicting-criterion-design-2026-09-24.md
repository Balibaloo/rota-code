# Design record: the Tester sends a criterion that contradicts the request back (frame 81)

Written by the assistant, session 2f969272, on 2026-09-24 08:00, for a
design review before any code. Revision 2 at 08:15 folds the design
review's twelve findings (observed: the reviewer on Opus 5.5, 129k on the
harness line, 55 tool calls, three probes). Meta workflow for the build.
Rota workflow for the fault. The tree is `693c9c8`.

## The fault (observed: night 91, `.rota/clickI_night91_walk1.db`, 2026-09-24)

1. The request, statement `s1` and item `bg_1`'s text: "Add an
   echo_json(obj, indent=2) helper next to echo that prints an object as
   JSON." Ticket `tk_1` carries the same words. Criterion `c_1`, written
   by the Terminologist: "echo_json returns a string containing the JSON
   representation of obj, formatted with indent=2."
2. The Tester `s144`'s recorded turn 2 says "I will now triage each
   criterion as `encodable` and encode its test in a single reply", and
   no completion of the session says "prints" about `c_1` (observed: the
   design review's read of turns 1 to 8). It triaged `c_1` `encodable` and
   encoded `tst_echo_json_returns_string`. A replay of turn 2 with recall
   questions, which is a counterfactual run and not the recorded session,
   shows the seat can quote both spans and name the disagreement when it
   is asked (observed: `probes/frame37/interview_turn.py`, 2026-09-24
   05:15). So the seat can see the contradiction and did not act on it.
3. The Developer built to the test, saw the same disagreement, and
   challenged the Tester seven times. The runner refused six as repeats.
   The criterion's owner is the Terminologist, and no route from the
   Developer reached it. The batch spent twelve attempts on a diff that
   could not satisfy both the request and the test.

## Why the verdict is missing (observed: `rota/core/sandbox.py:104`, `rota/roles/api.py:3900-3990`, 2026-09-24)

- `tests.triage` accepts five verdicts: `encodable`, `cannot`,
  `ambiguous_word`, `no_machine_check`, `outside_fact`. The brief's one
  judgement is "could a machine check this sentence?" Every verdict
  answers that question. `c_1` is a sentence a machine can check, so
  `encodable` was the honest answer to the wrong question.
- `cannot` sends a question to the Terminologist. The Terminologist's
  `question` mode answers and cannot amend: its tools are lookups and the
  three answer channels (observed: `terminologist/question.tools`). The
  criterion is rewritten only by `criterion_repair`, which fires on a
  Tester question with status `unresolved` that names a criterion
  (observed: `rota/core/predicates.py:1045-1070`). A question reaches
  `unresolved` through `schedule.reask`, after an answer that did not
  land (`api.py:5711`). So the shortest route today from "I see the
  contradiction" to a rewrite is three sessions: question, answer, reask.
- `tests.encode`'s prints-or-returns wall (`api.py:4821-4856`) reads the
  criterion's own words first. `c_1` says returns, so the wall let a test
  on the return value through. The wall compares the test with the
  criterion, and nothing compares the criterion with the request.

## The design: a sixth verdict, and the question is born unresolved

### 1. The verdict (`rota/core/sandbox.py:104`, `rota/roles/api.py:3900`)

- `ENUMS_BY_OP[("tests", "triage")]["verdict"]` gains
  `contradicts_request`.
- `tests_triage` gains two optional parameters, `request_span: str | None
  = None` and `criterion_span: str | None = None`. The verdict
  `contradicts_request` requires both. Any other verdict refuses a span:
  "a span belongs to contradicts_request; if the criterion agrees with
  the request, send the verdict alone".
- **The request's words are three rows, in this order**: the statements
  the item rests on (`refs` from `items` of kind `statement` to
  `statements`, not superseded, which is where `batches.expect` builds
  "the principal said", `api.py:9243-9248`), the item's `text`, and the
  ticket's `text`. The ticket is the Vision Keeper's slice and a seat's
  derivation, so it is last and it is named as a ticket. `request_span`
  must be a substring of one of them, and the note names the row it was
  found in. `criterion_span` must be a substring of the criterion's
  `text`.
- The comparison strips outer quote marks and final punctuation from the
  span, lowercases both sides, and collapses whitespace. Nothing else. A
  span not found is refused, naming the side: "request_span is not in the
  statements, the item or the ticket. Copy the span from the request's
  words, not a paraphrase". This is the parroting guard's shape. The
  reason is the composition's: every claim cites a source, and a seat can
  check the claim against the source.
- On a verdict that passes, the op stages one outbound message in
  `ctx.outbound`: from the Tester to the Terminologist, verb `question`,
  `body_refs` the criterion id and its ticket id, `cause_id` the trigger,
  `status` `unresolved`, `unresolved_note` in one form: `s1 says 'prints
  an object as JSON' and c_1 says 'returns a string'. Both cannot hold.`
  The row carries a tag, `route: "triage"`. The model does not send the
  message itself: the verdict is the route, by construction, and a route
  the model has to take in a second call is the route `s144` did not
  take.
- **The tagged row is exempt from the question replace step and the
  duplicate guard** (`sandbox.py:1447-1452`, `:1710-1716`). The review's
  probe put the row in `ctx.outbound` and showed a later
  `msg.question_terminologist` refused as a duplicate, and a later
  `msg.question_vision_keeper` removing the row. Both steps skip a row
  with the tag.
- **One row per criterion.** The op stages nothing when `ctx.outbound`
  holds a tagged row for the criterion, or when an open or unresolved
  Tester question already names it (the query at `api.py:3976-3984`). It
  then returns the existing "already asked" sentence.
- **The verdict withdraws a test staged earlier in the session for the
  same criterion.** The verified spans are the evidence, and the order of
  the calls is not (compare the comment at `sandbox.py:1454-1471`, which
  removed an order-based guard; this one is evidence-based). The return
  names the withdrawn test id.
- The op returns `next`: "routed: c_1 goes to the Terminologist to be
  rewritten before any test exists. Encode the others or end the session".
- `tests.encode` on that criterion is refused already, because the
  verdict is not `encodable` (`api.py:4096`). No change there.

### 1a. The wall at `encodable` on the one measured pair

`PRINTS` and `RETURNS` move from `tests_encode` to module level and both
sites read them. At `tests.triage(verdict='encodable')`, the op reads the
criterion's own words and the request's words (the same three rows as
above, joined). When one side holds a `RETURNS` word and no `PRINTS`
word, and the other side holds a `PRINTS` word and no `RETURNS` word, the
verdict is refused: "c_1 says 'returns' and s1 says 'prints'. That is
contradicts_request, with request_span='prints' and
criterion_span='returns'". The refusal quotes the two words it found, so
the retry can copy them. Why a wall and not the brief alone: the recorded
`s144` never said "prints" about `c_1`, so a brief line is a prediction
about a 9B model, and a prediction never gates (reasoned: the design
review's finding 6). The wall is one word pair, the pair every night
since 42 has stumbled on (observed: the comments at `api.py:4825-4835`).
The general case stays with the verdict and the brief.

### 2. A message born unresolved (`rota/core/db.py:256`, `:589`, `rota/core/runner.py:3267`)

- `OutboundMessage` gains `status: str = "open"` and `unresolved_note:
  str | None = None`. `session_commit`'s insert writes both columns.
  `_messages_from` passes both through from the staged dict. Every other
  constructor builds by keyword and every raw inserter leaves `status`
  out, so the schema default holds and no recorded row changes (observed:
  the design review, finding 9).
- The schema's comment on `unresolved` says "answered, and the asker says
  it did not land". A message born unresolved is the same state with the
  answer skipped: nobody owes a reply, and the asker has already said
  what is missing. One sentence is added to the schema comment. The word
  is reused rather than a fifth status added: the review ran every
  registered predicate on a row born unresolved, and only
  `criterion_repair` (fix band, detail = the note) and `tests_missing`
  (naming the other criteria) fired; `unresolved` yielded nothing;
  `scheduler.waiting_on` reads `open` only; audit rule 5 reads answered
  rows only (observed: the design review, findings 2 and 10). A new
  status costs a table rebuild and about seven readers for nothing.
- The `answered` sweep in `session_commit` (`db.py:611-616`) marks an
  unresolved message answered when another role speaks in its thread. The
  repair session answers the Tester with `msg.answer_tester`, so the row
  closes the way the brief already says it does.

### 3. The predicates (`rota/core/predicates.py`)

No predicate changes. The pinned tests below prove each reader on the new
row.

### 4. The briefs

- `rota/roles/prompts/tester/tests_missing.md`, after the `cannot`
  sentence: "A criterion can say a thing that the request does not say.
  Give it the verdict `contradicts_request`. Copy `request_span=` from the
  request and `criterion_span=` from the criterion. The verdict sends the
  criterion to the Terminologist. Do not encode a test for it."
- `rota/roles/prompts/terminologist/criterion_repair.md`, before the
  Vision Keeper paragraph: "The note can quote the request against the
  criterion. The request comes before the criterion. Rewrite the criterion
  to say what the request says. Keep the other words of the criterion. If
  the request is not clear, send `msg.challenge_vision_keeper`." The
  second sentence applies the composition's "intent flows down: Principal,
  Liaison, records, seats" (reasoned: a criterion is a seat's derivation of
  the request, so the request is upstream). It decides which row wins in a
  conflict, so it is named in the frame's status for Roman's check.

### 5. The tests

Pinned, in `tests/rota/test_triage_fork.py`. The fixture gains
`head_commit` on the batch and a second criterion `c2`, and the night 91
words on `c1`, its ticket and its item, with one statement row and its
ref:

1. `contradicts_request` with both spans stages one tagged message to the
   Terminologist, status `unresolved`, refs `c1` and `t1`, note naming
   `s1` and carrying both spans; `tests.encode` on `c1` is refused in the
   same session.
2. A `request_span` not in the statements, the item or the ticket is
   refused naming the request side. A `criterion_span` not in the
   criterion is refused naming the criterion side. A span with
   `encodable` is refused. A span with outer quotes and a final period
   passes.
3. After commit through `runner._messages_from` and `db.session_commit`,
   `criterion_repair(conn)` wakes the Terminologist with the note as
   detail, `tests_missing(conn)` names `c2` and not `c1`, and
   `unresolved(conn)` yields nothing.
4. A second `contradicts_request` on `c1` in the same session stages no
   second row. A later `msg.question_vision_keeper` on `c2` leaves the
   tagged row in place and lands beside it.
5. A test staged for `c1` before the verdict is withdrawn, and the return
   names it.
6. `encodable` on `c1` is refused by the wall, quoting `returns` and
   `prints`; `encodable` on `c2`, whose words agree with the request, is
   accepted.
7. `test_the_verdict_vocabulary_is_closed` grows by the new word.

The testkit: `capture` in `rota/testkit/fixtures.py:386` selects `status`
as well, and the message spec at `:568-579` reads an optional `status:`
key. Without it a cold case cannot tell the new verdict from `cannot`
(observed: the design review, finding 5).

Cold, in `tests/rota/cases/l1_tester.yaml`, one case,
`L1-TS-a-criterion-that-contradicts-the-request-goes-back`: tick
`tests_missing`, the night 91 request as the statement, the item and the
ticket, `c_1`'s text as the one criterion, batch running with a head
commit. Expect one question to the Terminologist with the criterion in
refs and `status: unresolved`. Forbidden: writes to `tests`, `criteria`,
`items`. Recorded through the register like every case.

**The stale set the gate will name** (observed: the design review,
finding 9): the brief edits change the prompt of every `tests_missing`
case (`l1_acts` 3, `l1_judgement` 1, `l1_tester` 2) and every
`criterion_repair` case (`l1_tester` 1, `l1_unresolved` 1). Eight cases
re-record after the build, plus the new one.

### 6. The night

A warm night from `b79882e`'s snapshot or later, from a worktree at the
frame's closing commit. Ends when `c_1` of this request reaches the
Terminologist with no test on file, and the rewritten criterion has a
test after. Frames 79 and 80 share the night.

## Out of scope, recorded for the next frame that meets them

- The Developer has no route to the Terminologist for a criterion it
  disagrees with. It challenged the Tester seven times on night 91. And
  `tests_triage` returns early when a committed test already encodes the
  criterion (`api.py:3928-3932`), so once a wrong test has landed no later
  Tester session can send the criterion back. Frame 38's walls 2 and 3
  and this route are not this frame.
- `tests.encode`'s refusal says "has no triage verdict from you yet" for
  a criterion triaged `cannot` in the same reply (observed: `s144`'s
  runner account). The sentence is wrong for that case and it is not the
  wall.
- The repair session's Vision Keeper exit cannot leave the question
  unresolved: any message the session sends shares the question's thread,
  and the `answered` sweep (`db.py:612-616`) and the trigger rule
  (`runner.py:1995`) both mark the row answered (observed: the design
  review, finding 11, by reading). The brief promises what the pipeline
  undoes. The new route inherits it. One line for the next frame that
  touches the sweep.

## Price (reasoned: frame 77's shape, in `plans/operating-facts.md`)

Design record and review 110k, build 110k on Opus, diff review 90k, gate
15k, night 20k here and about two hours wall. Actual so far: the design
review 129k on the harness line.
