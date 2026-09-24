# Design record: the Tester sends a criterion that contradicts the request back (frame 81)

Written by the assistant, session 2f969272, on 2026-09-24 08:00, for a
design review before any code. Meta workflow for the build. Rota workflow
for the fault. The tree is `0978560`.

## The fault (observed: night 91, `.rota/clickI_night91_walk1.db`, 2026-09-24)

1. The request, ticket `tk_1`: "add an echo_json(obj, indent=2) helper
   next to echo that prints an object as JSON". Criterion `c_1`, written
   by the Terminologist: "echo_json returns a string containing the JSON
   representation of obj, formatted with indent=2."
2. The Tester `s144` read both, said in its own words that the request
   says prints and `c_1` says returns a string, triaged `c_1`
   `encodable` and encoded `tst_echo_json_returns_string` (observed: the
   interview probe on `s144` turn 2, 2026-09-24 05:15, and the `tests`
   table).
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
  The Tester took the one-session route instead, and it was the wrong one.

## The design: a sixth verdict, and the question is born unresolved

### 1. The verdict (`rota/core/sandbox.py:104`, `rota/roles/api.py:3900`)

- `ENUMS_BY_OP[("tests", "triage")]["verdict"]` gains
  `contradicts_request`.
- `tests_triage` gains two optional parameters, `request_span: str | None
  = None` and `criterion_span: str | None = None`. The verdict
  `contradicts_request` requires both. Any other verdict refuses a span:
  "a span belongs to contradicts_request; if the criterion agrees with
  the request, send the verdict alone".
- Each span is checked against the material before anything is staged.
  `criterion_span` must be a substring of the criterion's `text`.
  `request_span` must be a substring of the ticket's `text` or of the
  item's `text` (the principal's words that `batches.expect` shows). The
  comparison lowercases and collapses whitespace, and nothing else. A
  span not found is refused, naming the side: "request_span is not in
  the request's words. Copy the span from the ticket or the item, not a
  paraphrase". This is the parroting guard's shape, and the reason is the
  composition's: every claim cites a source, and a seat can check the
  claim against the source.
- On a verdict that passes, the op stages one outbound message: from the
  Tester to the Terminologist, verb `question`, `body_refs` the criterion
  id and its ticket id, `cause_id` the trigger, `status` `unresolved`,
  `unresolved_note` in one form: `the request says 'prints an object as
  JSON' and c_1 says 'returns a string'. The request is the principal's
  words.` The model does not send the message itself: the verdict is the
  route, by construction, and a route the model has to take in a second
  call is the route `s144` did not take.
- The op returns `next`: "routed: c_1 goes to the Terminologist to be
  rewritten before any test exists. Encode the others or end the session".
- `tests.encode` on that criterion is refused already, because the
  verdict is not `encodable` (`api.py:4096`). No change there.
- The existing "already asked" branch at `api.py:3976-3986` applies: a
  second session that triages the same criterion while the row is
  `unresolved` is told the question is travelling.

### 2. A message born unresolved (`rota/core/db.py:256`, `:589`, `rota/core/runner.py:3271`)

- `OutboundMessage` gains `status: str = "open"` and `unresolved_note:
  str | None = None`. `session_commit`'s insert writes both columns. The
  runner's conversion of `ctx.outbound` to `OutboundMessage` passes both
  through. Every other channel stays `open` with no note, so no recorded
  case changes its rows.
- The schema's comment on `unresolved` says "answered, and the asker says
  it did not land". A message born unresolved is the same state with the
  answer skipped: nobody owes a reply, and the asker has already said
  what is missing. One line is added to the schema comment. The word is
  reused rather than a fifth status added, because every reader of
  `unresolved` is the reader this route needs: `criterion_repair` wakes
  the writer, `tests_missing` keeps the criterion out of the next Tester's
  wake, and `unresolved` cedes the Tester's criterion questions to the
  repair and resumes the ladder after one attempt (observed:
  `predicates.py:693-697`, `:975-978`, `:1045-1070`).
- The `answered` sweep in `session_commit` (`db.py:611-616`) marks an
  unresolved message answered when another role speaks in its thread. The
  repair session answers the Tester with `msg.answer_tester`, so the row
  closes the way the brief already says it does.

### 3. The predicates (`rota/core/predicates.py`)

No predicate changes. The pinned tests below prove each reader on the new
row:

- `criterion_repair` yields a Terminologist wake whose detail is the note.
- `tests_missing` no longer names the criterion while the row is
  unresolved.
- `unresolved` yields nothing for the row until a repair session has
  committed on it.

### 4. The briefs

- `rota/roles/prompts/tester/tests_missing.md`, one line after the
  `cannot` sentence: "A criterion a machine could check that says
  something the request does not is `contradicts_request`, with
  `request_span=` copied from the request and `criterion_span=` copied
  from the criterion. It goes to the Terminologist before any test
  exists. Encode nothing for it."
- `rota/roles/prompts/terminologist/criterion_repair.md`, one line: "A
  note that quotes the request against the criterion's words: the request
  is the principal's words, and the criterion follows them. Rewrite the
  criterion to what the request says, and keep its other words" (reasoned:
  the composition says intent flows down from the Principal, and a
  criterion is a seat's derivation of the request; if the request itself
  is wrong, the brief's existing exit to the Vision Keeper stands).

### 5. The tests

Pinned, in `tests/rota/test_triage_fork.py`, on the fixture the file
already has, with the night 91 words:

1. `contradicts_request` with both spans stages one message to the
   Terminologist, status `unresolved`, refs the criterion and its ticket,
   note carrying both spans; `tests.encode` on the criterion is refused in
   the same session.
2. A `request_span` not in the ticket or the item is refused naming the
   request side. A `criterion_span` not in the criterion is refused naming
   the criterion side. A span with `encodable` is refused.
3. After commit, `criterion_repair(conn)` wakes the Terminologist with the
   note as detail, `tests_missing(conn)` names no criterion for the batch,
   and `unresolved(conn)` yields nothing.
4. `test_the_verdict_vocabulary_is_closed` grows by the new word.

Cold, in `tests/rota/cases/l1_tester.yaml`, one case,
`L1-TS-a-criterion-that-contradicts-the-request-goes-back`: tick
`tests_missing`, the night 91 request as the item and the ticket, `c_1`'s
text as the one criterion, batch running with a head commit. Expect one
question to the Terminologist with the criterion in refs. Forbidden:
writes to `tests`, `criteria`, `items`. Recorded through the register like
every case.

### 6. The night

A warm night from `b79882e`'s snapshot or later. Ends when `c_1` of this
request reaches the Terminologist with no test on file, and the rewritten
criterion has a test after. Frames 79 and 80 share the night.

## Out of scope, recorded for the next frame that meets them

- The Developer has no route to the Terminologist for a criterion it
  disagrees with. It challenged the Tester seven times on night 91. Frame
  38's walls 2 and 3 and this route are not this frame.
- `tests.encode`'s refusal says "has no triage verdict from you yet" for
  a criterion triaged `cannot` in the same reply (observed: `s144`'s
  runner account). The sentence is wrong for that case and it is not the
  wall.
- The sandbox refuses a second `question` to the same recipient in one
  session (`sandbox.py:1711`). The staged route in section 1 does not
  pass that guard, so a session with two contradicting criteria stages
  two rows. Whether the guard should apply is a question for the review.

## Price (reasoned: frame 77's shape, in `plans/operating-facts.md`)

Design record and review 110k, build 110k on Opus, diff review 90k, gate
15k, night 20k here and about two hours wall.
