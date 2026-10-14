# Frames 187 and 219, the scope read: the decision under the item's own id

Read-only read at HEAD fccfc704, 2026-10-14, by one agent on Opus. Meta
workflow for this record. Rota workflow for every fact about the seats.
The databases were opened `mode=ro`. Tracked files were read through
`git show HEAD:<path>`, because `rota/roles/api.py` has uncommitted edits.

## 0. The answer in brief

1. The wall on night 147 is the `supersedes` argument, not the id. Each
   session moved to a new id after the first refusal. Then
   `supersedes="defines_commands_and_options"` met `_must_exist(ctx,
   "decisions", supersedes)`, and that refusal reads as a refusal of the
   `id` (observed: s287 turns 4 to 8, `.rota/clickI_night147.db`).
2. The night 147 read is wrong on two facts. The second refusal is not an
   update. s288 and s292 did report, m138 and m142 (observed: `messages`).
3. Frame 187's first mechanism silences 0 of 30 contested wakes on nights
   135 and 147. No contested wake fell inside an open Vision Keeper report
   thread on nights 135, 145, 146 or 147 (observed: the tables, this read).
4. Frame 219's first part is landed: commit 7b0a9aac, 2026-10-12, the
   author check in `decisions_author`. It is tested only on a Developer's
   row, `test_20_...` in `tests/rota/test_desk_guards.py:1740`.
5. The root of night 147's three wakes is s285's contest, which the
   principal never gave. Frame 238's door, landed at 252feb0e and pass 1b,
   now refuses that contest (observed: `plans/stack.md`, frame 238).

## 1. The chain on night 147, with the refusal texts

Timeline (observed: `sessions`, `messages`, `tick_attempts` of
`.rota/clickI_night147.db`):

| seq | session | wake | result |
|---|---|---|---|
| 285 | vision_keeper | relay m136 | contested `defines_commands_and_options`, an approved item the relay did not name (frame 238) |
| 287 | vision_keeper | `tick:contested` | 0 writes, no report |
| 288 | vision_keeper | `tick:contested` | report m138, round 1, at its last turn |
| 289 | liaison | m138 | clarify m139 to the principal |
| 290 | liaison | m140 | ruled "please leave it as it is" as `contest`, r_501a8b541b, relay m141 |
| 291 | vision_keeper | relay m141 | |
| 292 | vision_keeper | `tick:contested` | report m142, round 0, at its last turn |
| 293 | liaison | m142 | relay m143, no question to the principal |
| 299 | liaison | `tick:quarantined` | key `vision_keeper\|tick:contested\|defines_commands_and_options`, attempts 3, quarantined 1 |

s287's calls, in order (observed: `tool_calls` and `turns`):

1. `problem.consult()`. The pre-run had already given the result.
2. `transcript.quote(entry_id="defines_commands_and_options")`, which
   returned `{}`. The seat never saw words from the principal, because a
   tick wake carries no message and the principal said nothing.
3. `decisions.author(id="defines_commands_and_options", text="Users define
   commands and options ...", refs=["defines_commands_and_options"],
   supersedes="defines_commands_and_options")`. Refused:

   > `'defines_commands_and_options' is already a row of items; an artefact id is unique across every artefact table, or every ref to it is ambiguous. Give this decisions row an id of its own, a short name for what it says, and send again`

   This text comes from the sandbox wrapper, `rota/core/sandbox.py:3961`,
   before `decisions_author` runs.
4. The seat followed the text. `decisions.author(id=
   "defines_commands_and_options_defense", ...,
   supersedes="defines_commands_and_options")`. Refused:

   > `no decisions row with id='defines_commands_and_options'; this changes an existing row, so the id has to be one you were given; decisions rows are ['cj_compact_criterion', 'cj_serializable_criterion', 'd_184a233600', 'd_1a60e73b8c', 'd_2416ada0f4', 'd_26efd6365c']`

   This text is `_must_exist` at `api.py:513`, called for `supersedes`.
   It says `id=` and "this changes an existing row", so it names the
   wrong argument.
5. Turns 5 to 8: the seat took an id from the list,
   `id="d_26efd6365c"`, and kept `supersedes` on the item. The same
   refusal came back. Then the runner's note: `decisions.author has been
   refused the same way in three turns and will not be accepted again.`
6. The session ended with the account `named an act and did not perform
   it` and `ended a tick with nothing done`.

s288 ran the same chain, 6 sandbox refusals and 12 `_must_exist`
refusals, then `msg.report_liaison(refs=["defines_commands_and_options"],
round_no=1)`. s292 ran it with ids `dco_defines_commands` and
`d_1a60e73b8c`, 5 and 9 refusals, plus one `problem.assert`, refused:

> `defines_commands_and_options is the account's observed row and these are its words. Asserting it again makes what the repository already does a thing to build. Assert only what the principal asked for; an observed item stays observed until their words change it`

Then s292 sent `msg.report_liaison(..., round_no=0)` (observed).

Two facts matter for frame 219. `d_26efd6365c` and `d_1a60e73b8c` are
principal rows, "default taken at signoff" and "overruled at signoff"
(observed: `decisions`). s287, s288 and s292 aimed writes at them. The
`supersedes` refusal fired first, so the author check never had to act.

Across nights, `decisions.author` with `supersedes` set to an items id
(observed: `tool_calls`, this read):

| night | calls | sessions |
|---|---|---|
| 135 | 34 | 9 |
| 145 | 4 | 1 |
| 146 | 11 | 4 |
| 147 | 15 | 4 |

## 2. The mode and the brief on that wake

The wake runs `rota/roles/prompts/vision_keeper/contested.md` with
`contested.tools`: `problem.consult`, `problem.assert`,
`transcript.quote`, `decisions.search`, `decisions.author`,
`msg.report_liaison` (observed: HEAD). Last change 5e2f0e57.

The brief gives two routes and one fallback:

- The principal said what instead: `problem.assert` on the item's id.
- The principal said no and not what instead: "defend it once:
  `decisions.author` with the reason this item stands as written, then
  `msg.report_liaison`".
- "If you cannot tell *what* they objected to ... `msg.report_liaison`
  and say which of the three you need."

The brief assumes words: "What they said is in front of you:
`principal_said` in the message that woke you". A tick wake has no
message (observed: s287 `trigger_msg` is None, `transcript.quote` gave
`{}`). The brief says nothing about an observed item, and nothing about
`supersedes` (observed). The seat's reading in its completions was the
defend route. It wrote "the original wording stands", which is the second
bullet, and it added `supersedes` with the item's id in 15 of 15 calls.

## 3. The door at HEAD and frame 219's state

`decisions_author`, `rota/roles/api.py` at HEAD (the map prints the
working tree's lines, 9342-9441; HEAD has the `def` at 9302):

- The cross-table guard is in `rota/core/sandbox.py:3930-3968`, not in
  `decisions_author`. Its text names one step: "Give this decisions row an
  id of its own". It names no report. The seat obeyed it on the next turn
  in 3 of 3 sessions (observed).
- The "minuted" guard refuses an id built from an item amended this
  session. It did not fire on night 147, because no session amended.
- `if supersedes and supersedes not in staged: _must_exist(ctx,
  "decisions", supersedes)`. This is the wall.
- The author check, frame 200's pass 5 fix 7:

  ```python
  owner = ctx.conn.execute("SELECT author FROM decisions WHERE id = ?",
                           (id,)).fetchone()
  if owner is not None and owner["author"] and owner["author"] != ctx.role:
      raise ValueError(
          f"{id} is a decision by {owner['author']}. A decision is its "
          f"author's record, so write yours under a new id.")
  ```

Frame 219's first part is landed at **7b0a9aac**, 2026-10-12 17:06,
"feat(core): a Developer challenge carries its reason as the Developer's
own decision row" (observed: `git log -S "write yours under a new id"`).
The refusal, not a new version, is the shape. Its one test is
`test_20_a_vision_keeper_cannot_write_under_the_developers_reason_id`,
`tests/rota/test_desk_guards.py:1740`, on a Developer's row. No test
names a principal row or night 143's calls (observed: grep of `tests/`).
Sessions whose turns show the refusal "is a decision by": 6 on night
145, 1 on night 146, 2 on night 147 (observed: `turns`). Frame 219's
second part, a night count of overwritten principal rows, needs two
copies of one night's database. This read did not count it.

Night 143's four overwrites, the calls at HEAD (observed:
`.rota/clickI_night143.db`, `tool_calls`):

- s278: `id='d_a54ff9743f'`, `supersedes='d_a54ff9743f'`.
- s415: `id='d_d5e7673701'`.
- s443: `id='d_04589009a6'`, `refs=['tst_version_option_show_python']`,
  wake `message` m293.
- s467: `id='d_1b0161775a'`, `supersedes='d_33f8c35a52'`, four times.

Each id holds `author='principal'` (observed: `plans/night143-read.md`,
section 7, copied with its mark). At HEAD the author check refuses all
four (reasoned: the rows' author is `principal`, the seat's role is
`vision_keeper`). Two gaps stay (reasoned, not run): a row with an empty
author passes, and a seat overwrites its own role's rows.

## 4. The predicate

`contested`, `rota/core/predicates.py:291-305` at HEAD, reads
`items.approval = 'contested'` and `not_parked(conn, "id")`. It reads no
report, relay or message. The last change is 61a0f41d, frame 193's pass
2, which added `not_parked` (observed: `git log -L`). Frame 142 is closed
in `plans/archive/stack-2026-10-09.md`. Its sites are the walk, the park
ask and `rulings.rule`. It did not touch this predicate (observed: the
line history shows no frame 142 commit).

Frame 187's text says the tick fired "three more times between the
report and the relay" on night 135. The tables do not show that
(observed: `.rota/clickI_night135.db`, this read):

- s103 reported m20. s104, s105 and s106 took m20, m22 and the relay m23.
  No contested wake ran between s103 and s106.
- s115, s116 and s117 woke after s106 had taken the relay. s117 then
  reported m30. s118 and s119 took m30 and the relay m31. No contested
  wake ran between them.

Contested wakes that fell inside an open Vision Keeper report thread on
the item: night 135, 0 of 24; night 145, 0 of 1; night 146, 0 of 19;
night 147, 0 of 6 (observed: a script over `sessions` and `messages`,
the thread open from its producer's session to the last consumer). On a
walk, every message is taken before the next tick, and the scripted
principal answers at once. So the guard can only act when a person takes
time to answer a clarify (reasoned: the order in the tables). No night
measures that case.

The re-wakes have two causes. First, every session ends with nothing
landed, so the item stays `contested`. Second, a report's round ends
with the item still `contested`: s290 ruled "please leave it as it is"
as `contest` (observed: the night 147 read, section 6, copied with its
mark).

## 5. The records' rulings on the route

- `rota/LAWS.md`, law 11: "A challenge to an `observed` or `reasoned`
  entry forces its first ruling." "The Liaison writes a ruling as a
  record with a version." A contest of an observed item ends in a ruling,
  and only the Liaison writes one. The route that reaches the Liaison is
  `msg.report_liaison`.
- `rota/LAWS.md`, law 14: "A ruling in `decisions` is a record. Its
  identity derives from its content, and it carries a version." This
  rules frame 219: an overwrite under an id breaks law 14.
- The contested brief: defend once with `decisions.author`, then
  `msg.report_liaison`. With no words, report.
- 81f27127, frame 221: the route text "A decision has no supersedes for
  an item", after the re-record of
  `L1-VK-decide-a-challenge-to-an-approved-item` sent `supersedes` with
  the item's id in 3 of 5 runs, "and each refusal ended the session"
  (observed: the comment in `_assert_words_fault`, HEAD). The same seat
  habit is the night 147 wall, on a mode where that text does not reach.
- 62c5c046 and 84ea995f: an observed item changes only by the
  principal's words. That is the `problem.assert` refusal s292 met.
- Frame 129 holds the sibling shape on a challenge: decision under a new
  id, then an assert. It is open and does not rule this route.
- `rota/DECISIONS.md` has no entry on an observed item or `supersedes`
  (observed: grep).

The answer to the brief's question: the records give both steps, in the
order the brief gives. A reason under an id of its own is allowed once.
The report is the step that ends the wake, because law 11 says the
contest of an observed item needs a ruling. So the refusal names the
report as the closing step.

## 6. The pass 1 shape, with the tests

One implementer, one pass, three sites. The `contested` predicate is not
a site: it would silence 0 of 30 measured wakes (section 4).

- **Site A, `decisions_author` in `rota/roles/api.py`.** Before
  `_must_exist(ctx, "decisions", supersedes)`, read whether `supersedes`
  is a row of another artefact table. If it is, refuse through `_offer`
  with the call again minus `supersedes`. Proposed text: "{supersedes} is
  a row of items, and supersedes takes the id of a decision. A decision
  has no supersedes for an item. Send decisions.author again without
  supersedes, under an id of its own. Then send msg.report_liaison, so
  the principal rules on {supersedes}." Name `msg.report_liaison` only
  when the mode's tools offer it, as frame 238's pass 1b did.
- **Site B, `rota/roles/prompts/vision_keeper/contested.md`.** One
  sentence after the "cannot tell" paragraph: on a tick, when
  `transcript.quote` gives nothing, you cannot tell what they objected to,
  so send `msg.report_liaison` and stop. This changes the brief hash.
  Re-record the Vision Keeper contested cases at the new hash.
- **Site C, `tests/rota/test_desk_guards.py`, frame 219.** No code. Two
  tests that pin the landed author check on a principal row.

Tests, red first where the code moves:

1. Site A, red: s287's turn 4 call, `id="defines_commands_and_options_defense"`,
   `supersedes="defines_commands_and_options"`, on a database where the
   item is a row. Red today on the text: the refusal says `no decisions
   row with id=`. Green: the new text, and the offered call has no
   `supersedes`.
2. Site A, red: s288's call with `id="d_26efd6365c"` and `supersedes` on
   the item. Green: the `supersedes` refusal, and no write.
3. Site A, green today and kept: the same call without `supersedes` on a
   principal row `d_26efd6365c` gives "d_26efd6365c is a decision by
   principal", and the row's text stays.
4. Site A, green today and kept: `supersedes` that names a real decision
   still lands.
5. Site C: night 143's s443 call, `id='d_04589009a6'` on a principal row,
   refused, row unchanged. s278's call with `supersedes` equal to its own
   id on a principal row, refused.
6. Site B: the contested recorded cases at the new hash, by exact id.

The gate runs once at the end of the pass. One diff review follows. The
next night measures: Vision Keeper contested sessions with every call
refused, from 3 of 3 on night 147.

## 7. The risk

- Site A refuses nothing that lands today. `supersedes` is a foreign key
  to `decisions`, so an items id fails `_must_exist` now (reasoned: the
  code). Wrongly refused: 0. Moved text: 64 calls over nights 135, 145,
  146 and 147 (observed, section 1).
- Site A can send the seat to an existing principal decision id. The
  author check refuses that, so no principal row is lost (reasoned).
- Site A can land a defence decision while the item stays `contested`.
  The tick then fires again until a report. The text names the report
  for that reason (reasoned). Count: unknown until a night.
- Site B can silence a defence the seat had reason to write. On a tick
  with no words, the brief already says to report (observed: the brief).
  Count of sessions wrongly sent to report on night 147: 0 of 3, because
  the principal never contested (observed: section 1).
- Site C adds tests only. It refuses and silences nothing.
- Not doing the predicate: a person who takes time to answer a clarify
  can get re-wakes while the report waits. No night measures it
  (reasoned: section 4). That case is a separate frame, measured on a
  night with a delayed principal.
- Frame 238 removes night 147's trigger. The next night may show 0
  contested wakes on an observed item, so the ratio can fail to measure.
  The closing night then needs a contest the principal really gives.

## 8. The tokens

About 70k on this read, by the agent's own count. The harness line is
the record.
