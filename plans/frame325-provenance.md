# Frame 325, the provenance: the page's notes section shows a Developer's account as his assumption

Provenance read, 2026-10-25, at HEAD 35ced282. Databases night 150 to
night 165 with 164a, opened `?mode=ro`. Meta workflow. No file but this one changed.

## The verdict

**The page reads no kind and no author of a ledger row. `_resolve_refs`
gives it `id, about_ref, default_taken` only, and `_page_body` numbers every
such row under "Where you did not say, I assumed:". Frame 204's design,
ruled "Start as written" on 2026-10-11 15:44, sends an `other` row to a quiet
section and writes no trace or echo. Its page pass was never built, so the
code departs from a ruled design. Kind `other` is a small part of the wall:
4 of the 19 accounts on a page are `other`, and 12 are `default`.**

Correction to the premise: only m172 carries `l_0553f217b1`. Line 6 of
m239 and m253 is a `default` row (observed: night 165, `messages`).

## 1. The mechanism today

- Selection: `tick_agenda` reads every open row and keeps every row that is
  no reply row, with no kind filter (observed: `rota/core/scheduler.py` 1142,
  1152). The present door adds up to seven open rows about the page's refs,
  with no kind filter (observed: `rota/core/sandbox.py` 3709 to 3718).
  `off_page` drops rows by request only (observed: `principal.py` 977 to 1018).
- Resolve: the ledger resolves to `id, about_ref, default_taken` (observed:
  `rota/core/runner.py` 2793). The page never sees `kind` or `author`.
- Render: any row with `default_taken` goes to `assumed` (observed:
  `rota/roles/principal.py` 1791). The page prints `TEAM_NOTES` and "Where
  you did not say, I assumed:", and numbers each row (observed: 1501, 1913 to
  1916). All seven ledger kinds get this one text.
- Writer of `other`: `ledger.log` offers `LOG_KINDS` with `other` last
  (observed: `rota/roles/api.py` 12460). Its text says "A note that fits no
  word is 'other'" and "A step, a plan or a ruling said again is no note: log
  nothing" (observed: 12494 to 12511). Only `_refuse_an_echo` enforces the
  second sentence, for a note about the row the waking relay ruled on
  (observed: 12941 to 12953).
- The wall's writer: s228, Developer, `tick:batch_start`, "attempt 2 of 3:
  the last session committed nothing", qwen3.5:9b (observed: `sessions`).
  `developer/batch_start.md` 42 to 48: "A choice the criteria did not make is
  a `ledger.log`", with "`blocked` or `fault` when rota itself stopped you,
  `other` when no word fits". s228 wrote a completion claim and a block. Neither is
  a choice. The block half had a word, `blocked`, which goes to `faults` and no page.

## 2. The origin

- The resolve without `kind` is c7a228de, 2026-08-09. "I assumed:" is
  d3d1e4b4, 2026-09-08, when the ledger had one kind. `TEAM_NOTES` is
  358fed11, 2026-10-09, frame 190. Kind `other` is b00aaa59 and 6307f965,
  2026-10-11, frame 204 passes 1 and 1b (observed: `git log -S`).
- The ruling: "they can reach me if they are shown quietly" (ruled: Roman,
  2026-10-11 15:00), then "Start as written" (ruled: 15:44, stack.md frame
  204). Section 5 is the page by category. Section 8: "An `other` row goes
  to the quiet section and to a count on the night read" (observed:
  `plans/frame204-design.md` 256 to 281, 372).
- Pass 3, "the page and the park", was frame 198's. Frame 198 closed on the
  park ratio alone (ruled: 2026-10-14 17:59). Frame 204 was parked on
  2026-10-21 with the page pass unbuilt (observed: its status of 16:23). So
  the kind reached the column and never the page.

## 3. The design's own condition

- The composition, Records: "A record says whether it was observed from the
  code or the world, reasoned by a seat, or decided by the Principal". Flows:
  "Every claim cites a source" (observed: `plans/composition.md` 45 to 80).
  An assumption is a choice where his words were silent, the `default`
  category (observed: frame 204 design, section 2, row 2).
- Frame 204 section 2 rows 7 and 8: a trace, "A step, a plan or a state. No
  choice", and an echo of a ruling are "Not written". Section 5: after intent
  under `auto`, a default is "listed, not numbered, in the request's quiet
  section". Conflict, a climbed scope and unaddressed stay numbered.
- Today's code departs in three places. The tick and the hook select every
  kind. The page numbers every kind under "I assumed". The door writes
  traces and echoes as `default` or `other`. m172 line 6 is an unchecked
  claim of state, worded as his assumption, and he answered it three times.

## 4. The count

Distinct ledger rows in the refs of a present to him, nights 150 to 165 and
164a (observed: `messages`, `ledger`): default 182, invented 104, conflict
57, scope 27, gap 17, unaddressed_answer 8, other 6. Total 401.

A pattern search for a seat's own work or state ("now calls", "I added",
"already satisfies", "per the principal", "blocked", "commit") found 34
rows. My reading of each gives a lower bound (reasoned):

- 19 rows are a seat's account of its own work or state: 4 `other`
  (l_b8edbfb7d6, l_8aa880d2b4, l_7e7cc4d680, l_0553f217b1), 12 `default`,
  2 `scope`, 1 `conflict`.
- 7 rows restate a ruling, the design's echo: 5 `default`, 2 `conflict`.
- 2 `other` rows are no account: l_8fd20d7618 is a test-against-code
  disagreement, and l_a9cfaa6bec is an observation about item text.

His replies that ask to remove a numbered line under the team's notes: 11
replies on 9 pages, a regex upper bound (observed: the principal jsonl of
nights 150 to 154, 164, 164a, 165). Nights 155 to 163 have no jsonl and are
not counted. On night 165, m172 has 3 replies on line 6, m239 and m253 one each.

## 5. The repair's shape

- **Candidate K, the page reads the kind, as frame 204 sections 5 and 8
  rule.** Add `kind` to the ledger resolve. `_page_body` numbers under "I
  assumed" only the kinds that section 5 numbers, and an `other` row
  becomes one quiet count line with no number. The tick and the hook stop
  waking a page for `other`. Red test: m172's refs render with no line "The
  batch is complete because ...". The first step takes 4 of 19 accounts off.
  The full section 5 scope, a `default` quiet after intent, takes 16 of 19,
  and it changes what he answers, so it is the ruled next pass. K reads a
  column that the seat named, not prose.
- **Candidate D, the door refuses a trace.** `ledger.log` refuses a note
  that states the seat's own work or state and names no choice, as section 2
  rows 7 and 8 rule. It catches accounts of every kind at the source. But
  the door must read prose to tell a trace from a choice, which is frame
  321's wall, a word set with no subject. It also costs a 9b seat one more
  refusal on its last attempts.

**Favoured: K.** It builds a design he ruled that nobody built. It reads a
column, not prose, so it fits the workflow and not this one row. The 15
accounts of other kinds that remain after K's first step measure the
section 5 default step, not D.
