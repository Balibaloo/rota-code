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
