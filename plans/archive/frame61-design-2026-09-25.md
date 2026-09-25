# Frame 61, an unmet obligation is visible only while something points back at it: design record

Revision 1, 2026-09-25, written by session 5748c2d9 from the scope report
`plans/archive/frame61-scope-2026-09-25.md` and the night 88 read
`plans/archive/night88-cut-read-2026-09-25.md`, section 6. Rota workflow.

## The fault

A seat is refused a write. The refusal is one `ERROR` line in a results block.
The next turns bury that block, and nothing restates it. The seat then either
never returns to the call, or reports the write as done. On night 88, seats
were refused on 110 session-and-call pairs, 66 were never met later in the
same session, and 14 of those owed a write or an act; for 9 the session had
later turns and the seat did not go back (observed: the night 88 read, section
6, 2026-09-25). In two turns a cut hid the refusal from the seat before it read
it (observed: the same section). The composition says nothing stops quietly and
every open obligation stays visible until something discharges it.

## The rule that constrains the design

No line may say where a thing sits in the prompt. "Above" and "below" are
forbidden (ruled: frame 61's block, from frame 46's re-earning pass). A wording
that points backwards scored 0 of 5 four times.

## What "met" means in code

No structure records a refused call and clears it on success. `ctx.refusals`
and `refused_same` are keyed by op name and never cleared (observed: the scope
report, section 3, `rota/core/sandbox.py:2001-2003`, `rota/roles/api.py:99`,
`rota/core/runner.py:2232`). So met means one thing: `sb.call` at
`rota/core/runner.py:2577` returns without an error for the same op name
(reasoned: the scope report, section 3, and the night 88 read's own definition).

## The design: an owed list joined after the cut

Design A of the scope report, section 7, with four decisions added.

1. **A runner dict `owed`**, op name to the reason and the turn number, beside
   `refused_same` at `rota/core/runner.py:2232`. An op enters it when a call
   raises in the `except` at `:2814` and the op is not a read (`call.name` not
   in `read_fns`) and the refusal is not the `Repeat` class. An op leaves it
   when `sb.call` returns for that op name, and when the `NOTE ... will not be
   accepted again` line fires for it at `:2834-2838`.
2. **One block, joined to `user` after `_fit`** at `:2243-2244`, and never
   stored in `transcript`. `_fit` receives `budget` less the block's length plus
   its separator, so `_prompt_overrun` at `:2248` stays quiet and both of
   `_fit`'s paths and `_cap_exchange` see the same room (reasoned: the scope
   report, section 4, points 1 to 3).
3. **The wording.** One line per owed op, oldest first, at most three ops:

   ```
   OWED <op>: refused earlier this session: <reason>. It is not done until a call of <op> returns OK. If it cannot be done, say so in one sentence and do not report it as done.
   ```

   The line starts with `OWED`, not `ERROR`, because `FABRICATED_RESULT` reads
   an echoed `ERROR` as an invented result and drops the turn's calls (observed:
   `rota/core/runner.py:510-511`). "Earlier this session" names a time and not
   a place. The last sentence exists because 49 of night 88's 66 unmet refusals
   close the matter by design, no code field tells those from the correctable
   ones, and a seat told to do a thing the op refuses again must have a way
   out (reasoned: the scope report, section 6, false obligations).
4. **The reason is kept whole up to 300 characters, and the tail wins.** Frame
   82's doors put the exact passing call at the end of the message, for
   example `send msg.report_liaison(refs=[...]) with the same refs`, so a cut
   that keeps the head drops the one sentence the seat needs. When the reason
   is longer than 300 characters the line keeps the last 300 (reasoned: the
   door texts in `rota/roles/api.py` at 2209-2274 and `rota/core/sandbox.py`
   at 1682-1698, read 2026-09-25). Cost per turn: about 120 characters of fixed
   words plus the reason, at most 420 per op and 1,260 for three, and 0 when
   nothing is owed.
5. **A session that ends with an owed op says so.** At the session's end, for
   each op still in `owed`, `outcome.errors` gains one line,
   `ended with a call still owed: <op>`. This is the countable trace the
   composition asks for, and it is what the new test asserts. The line starts
   with `ended`, so `fixtures.py`, which reads a dotted prefix as a refused
   call, does not mistake it (observed: the comment at
   `rota/core/runner.py:3103-3109`). It is added once at the end and never per
   turn (reasoned: the scope report, section 6, `outcome.errors`).
6. **What does not change.** `_fit`'s signature and its unit tests. The stored
   turn at `:2257` records the full `user`, so the line is in `turns.user` and
   in the per-turn cassette key. The wake's `prompt_hash` does not move, so no
   case reads stale; the per-turn keys after a refused write do move, so the
   cases with a refused write need a re-record (reasoned: the scope report,
   section 5).

## Why not design B

Design B puts the lines at the head of each results block. They survive the
results cut and cost nothing new in `_fit`, but each kept block carries a copy,
and the line is then not at the tail, which is the lever the frame names
(reasoned: the scope report, section 7).

## Tests

- New, in `tests/rota/test_runner.py`, on the scripted backend: a write is
  refused at turn 1, a read runs at turn 2, and the last line of
  `backend.calls[2][1]` names the owed op; after a successful call of that op
  at turn 3, `backend.calls[3][1]` carries no `OWED` line.
- New: a session that ends with the op still owed carries
  `ended with a call still owed: <op>` in `outcome.errors`, and a session that
  met it does not.
- New: a refused read and a `Repeat` refusal put nothing in `owed`.
- New: the `NOTE ... will not be accepted again` line clears the op.
- New: with three ops owed the block holds three lines, and a fourth op does
  not extend it.
- Moved: none of the four existing refusal tests named in the scope report,
  section 5, because the owed line is outside the results block (reasoned).

## Re-records and the walk

`ACT-TS-five-criteria-one-per-reply` first, then the other cases whose
recorded runs carry a refused write: the implementer lists them by a read-only
query over `case_runs` for transcripts with an `ERROR <write op>` line, and
re-records them by exact id in the foreground with `ROTA_MODEL=qwen3:8b`,
tallies before and after. A case that falls below its tally is a regression
and is named, not repaired, in the pass.

The frame touches the write pipeline, so it ends on a walk: one night from a
worktree at the closing commit, shared with frame 59, which the batch order
puts beside it, and read for two counts: refused writes met later in the same
session against night 88's 44 of 110, and sessions ending with an owed call
against night 88's 14.

## Price

Design review, about 60k on Opus. One implementer pass, about 80k on Opus,
the frame's priced repair, plus about 30 minutes of GPU for the re-records
and one gate. The walk shares night 94 with frame 59.

## Questions for the design review

1. Does keeping the last 300 characters of a reason ever drop the op's own
   name or the noun the reason is about? Read ten refusal texts from
   `rota/roles/api.py` doors and say which.
2. Is "not in `read_fns` and not the `Repeat` class" the right set, or does a
   class of refusal exist that owes nothing and is not a read? Read the
   refusal classes at `rota/core/runner.py:2814-2840`.
3. Does the end-of-session error line change any reader of `outcome.errors`
   besides `fixtures.py`: the three readers the comment at `:3103-3109` names?
4. Is there a path where `sb.call` returns without error for an op and the
   write still did not land, so the op leaves `owed` too soon?
5. Does the block's cost at a tight window, with `_MIN_EXCHANGE` at 2,000,
   push a prompt over `num_ctx` on the 8192 profile?

## Revision 2, 2026-09-25, after the design review

The design review on Opus 5.5 (71.6k on the harness line against 60k, 19
tool calls) confirmed all ten of its findings by reading or by probe. Revision
2 changes the design in eight places. Where a point below contradicts the
design above, this section wins.

1. **Key by call tag, not op name** (review findings 4 and 7). `owed` is keyed
   by `_call_tag(call)`, the op plus its identifying argument. A success clears
   an entry only when its tag matches. The newest recorded run of
   `ACT-TS-five-criteria-one-per-reply` holds seven `tests.encode` refusals
   naming three faults beside successful `tests.encode` calls, so an op-name
   key would clear the line the frame exists for (observed: the review's
   probe over `case_runs`, 2026-09-25).
2. **The set: any raise in the `except` at `:2814` for a non-read op, except
   `NotInWorkingSet`** (finding 2). The `Repeat` clause is dropped: the repeat
   branches run after `sb.call` returns and never raise, so the clause
   excluded nothing (observed: `rota/core/runner.py:2690-2760`).
3. **One helper for set and clear, called from both paths** (finding 9). The
   stood-by run at `:2379-2383` calls `sb.call` outside the `try` at `:2575`,
   so a held write refused there never enters `owed`, and an owed op met
   there stays owed and ends the session on a false line. `_note_owed(call,
   error)` and `_settle_owed(call)` run in the main loop and in the stood-by
   loop alike.
4. **The line's reason keeps the first 100 characters, then `...`, then the
   last 200** (finding 1). A tail-only cut loses the subject in 21 of 201
   door texts (observed: the review's AST scan of `rota/roles/api.py`).
5. **`_fit` gains a `reserve` argument that only the middle eviction and
   `_cap_exchange` subtract, never the wake room** (findings 5 and 8). Passing
   a smaller `budget` cut a 6,000-character wake to 6,043 of a larger one and
   evicted a pair, and `_fit` stores its result back into `transcript`, so
   the damage outlives the op (observed: the review's probe at budgets 10,391
   and 8,896). Design point 6 above, which kept `_fit`'s signature, is
   withdrawn. The reserve is clamped: when `budget - reserve` would fall
   below `_MIN_EXCHANGE`, the block is left out of that turn's prompt and
   `owed` keeps its entries. One new unit test on `_fit` for the reserve.
6. **A tag that is refused three times is abandoned** (finding 6). The `NOTE`
   at `:2833-2842` keys on `(op, why[:160])`, and door texts insert ids, so a
   changing reason never fires it, and the owed line would ask for a new try
   every turn to `max_iterations`. After the third refusal of one tag the
   entry is marked abandoned: no prompt line is written for it again, and
   the end-of-session line still names it. So the session neither loops nor
   stops quietly.
7. **The end-of-session line is added before `session_note` at `:3110`, and
   the failure path writes none** (finding 3). The readers of
   `outcome.errors` beyond `fixtures.py` are `triage.py:178`, which classes
   the line as `other`, `casestatus.py:277-284`, which finds no miss marker
   in it, and `talk.py:99`, which prints it (observed: the review, 2026-09-25).
8. **Cost and the re-record query corrected** (finding 10). The fixed words
   are about 200 characters with a 20-character op name, so one op costs up
   to about 500 and three about 1,500 per turn. The cap stays at three ops,
   oldest first. The re-record query searches `case_runs.transcript` for
   `"<op>: "` inside its `errors` list, because the errors are stored as
   `op: exc` and not as `ERROR op` lines.

Not changed: the wording's first and last sentences, `OWED` as the first
word, the block joined after `_fit` and never stored in `transcript`, the
tests listed above plus one on the abandon rule and one on the stood-by
path, the walk on night 94 with frame 59, and the price.
