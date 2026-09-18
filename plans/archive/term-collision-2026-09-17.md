# The term-collision loop on cold click nights (frame 34, 2026-09-17)

Rota workflow. The cause is read from the turns of nights 83 and 84 by a
reviewer-type agent, read-only, 109k on the harness line, 29 tool calls.
The three run databases are copies in the session scratchpad:
`clickI_night84.db` (3ab5c73, cold, sentence two), `clickI_night83.db`
(3ab5c73, cold, sentence one), `clickI_night82.db` (d4bf679, cold,
reached batches). Written by the assistant (rota-02, session 3b4093c6).

## The cycle (observed: night 84, sessions s270 to s272, the same from s108 on)

1. The Terminologist wakes on `tick:term_collision` with refs `group`
   and `group#src_click`. It calls `msg.report_liaison` and lands
   message m126. The runner refuses its `glossary.synthesise` as a
   summary of the readings.
2. The Liaison wakes on the report. Its prompt carries `prior_answers`:
   the earlier clarify m7 and the principal's words, the sentence's
   constraint text, which name no row. In `answering` mode it holds the
   three relay tools only. It calls `msg.relay_terminologist` three
   times verbatim and lands m127, cause m126, no body.
3. The Terminologist wakes on the relay. Its inbound holds `from`,
   `verb`, `refs` and `resolved_refs`, no `principal_verdict`. Its brief
   (`rota/roles/prompts/terminologist/relay.md:4`) tells it the ruling is
   `principal_verdict` in the message. It calls `glossary.adopt`, which
   the runner refuses: no landed ruling on the chain. It logs two ledger
   rows and ends. m127 is answered, nothing is open, no decision names
   the rows, and the tick fires again.

Night 82 never entered this path (observed: no `tick:term_collision`
session; its Terminologist survey of `src/click` was `none_found`, so
the glossary held one `group`). Night 84's survey found `Group` and
wrote `group#src_click`. Six other families fired the same tick on
night 84 and were discharged inside the tick session by
`glossary.same`; `group` alone took the report route.

## The cause (reasoned: from the turns and the code, three linked defects)

- **A. A words-only reply to a clarify lands a ruling with no per-item
  verdict** (observed: `rulings` row `r_m8`, `per_item='{}'`, status
  `landed`, no `config` key `verdict:m8`; `rota/roles/principal.py:738-767`
  writes `verdict:<id>` only when items remain). Nothing downstream can
  read a verdict, and the Liaison in `answering` mode has no tool to
  write its reading. The composition says the Liaison's confirmed
  reading is a record and the Principal's ruling is written by the
  Liaison. Here no seat can write it.
- **B. The relay's verdict lookup climbs one cause hop, to the report**
  (observed: `rota/core/runner.py:719-726`, `verdict_for(conn,
  row["cause_id"])`; every relay m101 to m129 has the report as cause).
  Even a per-item ruling on the clarify's reply would not reach the
  Terminologist.
- **C. `term_collision` counts a family as ruled only through
  `decisions.refs` or a superseded row** (observed:
  `rota/core/predicates.py:366-371, 410-411`); `glossary.adopt` writes a
  `refs` row of kind `ruling` and no decision (`rota/roles/api.py:1047`).
  After A and B land, an adopted family still fires. Plausible, not yet
  observed, since no adopt ever landed.
- **D. Between cycles nothing parks the collision** (observed:
  `predicates.py:400-405` suppresses on open messages only; the report
  and the relay are answered when their sessions end). This is why the
  loop is three sessions long and never stalls into an attempt cap.

Not the cause: the commits between d4bf679 and 3ab5c73. The predicate's
body, the one-hop relay fallback and `prior_answers` all exist at
d4bf679 (observed: `git diff d4bf679 3ab5c73 -- rota/core/predicates.py`
and `git show d4bf679:rota/core/runner.py`). Not the model: the
Terminologist did what its brief says, and the field was never sent.

## A second wall, not this frame (observed: night 84, s96 to s98)

`tick:observed_entries` is quarantined after three sessions produced no
parsable tool call. Night 82 reached its glossary ruling through that
tick (present m27, 24 refs, ruling `r_255b49e4f5`). Nights 83 and 84
have no glossary ruling at all. Frame 35.

## The fix brief (ruled: the assistant, in the smart zone, 2026-09-17)

The rule the fix serves: the Principal rules and the Liaison writes it;
the tool never rules for the Principal; every open obligation stays
visible until something discharges it (`plans/composition.md`,
Records and Flows).

1. **The Liaison writes the reading** (A). Add `rulings.rule` to
   `rota/roles/prompts/liaison/answering.tools`. In `answering.md`: before
   any relay, read the principal's words against the rows in `about`;
   when the words answer the question, write the verdict per row with
   `rulings.rule` on the ask, as your confirmed reading; when the words
   name none of the rows and answer nothing about them, do not rule and
   do not relay: write one `ledger.log` row on each `about` row saying the
   answer did not address the question, then stop. Never write a verdict
   the words do not carry.
2. **The relay carries the ruling** (B). The inbound of a relay carries
   `principal_verdict` when a landed per-item ruling exists anywhere on
   the chain from the relay to the ask, through `_verdict_of`'s walk
   (`rota/roles/api.py:967-985`), not one cause hop. One function for the
   runner's inbound (`rota/core/runner.py:703-726`) and for `_landed_ruling`.
3. **An adopted family is ruled** (C). In `term_collision`, an id with a
   `refs` row of kind `ruling` counts as ruled.
4. **A logged family is raised** (D). In `term_collision`, a family whose
   rows carry a ledger row from the Liaison saying the answer did not
   address the question counts as raised: the tick does not re-fire
   until a ruling or a supersession lands. The row stays visible in the
   ledger and in `outstanding`.

Pinned tests, one each: a clarify with two refs, a words reply that
names them, the Liaison rules, the relay's inbound carries
`principal_verdict` (1 and 2); a words reply that names none, the
Liaison logs and does not relay, `term_collision` does not wake (1 and
4); two senses with `refs` ruling rows and no decision, no wake (3).

Touched register cases: the Liaison's answering cases and the
Terminologist's relay cases. Re-record them and report before and after.

The walk: night 85 from a worktree at the closing commit, from sentence
two. It closes when the night reaches a batch and a commit, which is
frame 33's walk too. If frame 35's wall stops the night first, that is
the night's result and frame 34 stays validating.

## The diff review of 6895000, 2026-09-18

A read-only reviewer read the commit on a worktree, against eight
numbered points, 112k on the harness line against a 65k cap, 49 tool
calls. The reviewer built the night-84 fixture and ran the whole cycle
in a real sandbox. The probes are named in the reviewer's report.

The result, first and loudest: **the loop still closes on one common
answer** (observed: the reviewer's probe ran cycles two and three and
the tick fired each time). The fix breaks the loop when the ruling
approves at least one row. The loop closes again when the ruling
contests or revises every row. The deciding line is
`rota/core/predicates.py:456`, `if any(i in ruled for i in ids)`, fed
by `rota/roles/api.py:1033`, which writes the ruling ref for approved
rows only.

Parts B and the write pipeline hold. One function, `chain_verdict`,
serves the runner's inbound, `_verdict_of` and `_landed_ruling`, with
no second copy, and the walk terminates on a `seen` set (observed: the
reviewer's read). Both new writes go through `ctx.writes`, and both
tables are declared (observed: `ARTEFACT_TABLES` and `identity.py`).
The commit adds no raw SQL write.

Five of the six deviations hold. One does not: `rulings.rule` accepting
a clarify as the page fails at its boundary, because a clarify has no
numbered page and no open-status guard (observed: findings 2, 6 and 7).

### The five high findings

1. **A contest-only or revise-only ruling re-enters the loop**
   (observed: the reviewer ruled both rows `contest`, adopt skipped
   both, no ruling ref and no ledger row were written, and the tick
   fired on cycles two and three). Cycle two runs in `report` mode,
   whose tool list holds neither `rulings.rule` nor `ledger.log`, so
   the cycle cannot write a reading at all. The whole defect is one
   answer word away.
2. **The clarify door tells the Liaison to approve a row the words
   never named** (observed: `api.py:5004-5006` sets `order = order or
   refs`, and the refusal text says a line the reply does not contest
   is an approve). The reviewer landed an approve on both rows for the
   reply "what time is the meeting". The tool rules for the Principal
   at the one door the fix added.
3. **One signoff keypress on the parked ledger row discharges the
   collision for good** (observed: the reviewer parked the family, then
   approved the parking row on the agenda page, and `term_collision`
   read the row as ruled). A decision that records a non-answer becomes
   the record that nobody ruled. Contest does the same.
4. **The parking sentence must be exact** (observed: a paraphrase did
   not park and the tick fired again). The ledger id is a hash of the
   text, so every paraphrase writes a new row each cycle and the ledger
   grows without bound. The one mechanism that holds the family between
   cycles rests on a model copying seven words.
5. **Nothing enforces the ruling before the relay** (reasoned: the
   runner breaks an answering session as soon as `ctx.outbound` is
   non-empty, and the brief asks for two calls in one turn with the
   relay second). A model that relays first ends with no ruling. The
   register case is 5/5 on qwen3:8b today, so the brief holds, but no
   door holds it.

### The four lows

Finding 9 is the same line as finding 1: one approved sense silences a
family that still holds a live contested sense, whose only other reader
is the quarantined tick of frame 35. Finding 8 is an unfiltered read of
the chain's ruling, which grew with this commit's walk. Findings 6 and
7 are a clarify ruling that applies no state and a clarify page with no
open-status guard.

### The fix pass

Findings 1, 2, 3, 4, 5, 8 and 9 go to a fresh implementer, cap 110k,
with seven pinned tests. Findings 6 and 7 stay out (ruled: the
assistant, they are low and off the delivery path). The implementer is
fresh, not the one that wrote 6895000 (reasoned: a stated deviation
from one implementer per frame, since that agent died with its
session).
