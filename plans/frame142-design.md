# Frame 142, a park ask gets an answer that names no option: the scope and the design

Status: section 1 written by an Opus agent of session acb1f403 on
2026-10-08, before any code, read-only on the tree at adaf2504. Sections 2
to 6 rewritten by a second Opus agent of the same session on 2026-10-08,
after Roman's ruling of 23:25, read-only on the tree at fb5fbc5f. Both
workflows. Each line names its workflow where the two differ. The night
facts come from `.rota/clickI_night132.db`, `.rota/clickI_night133.db` and
`.rota/clickI_night121.db`, read with `mode=ro&immutable=1` by the scripts
in the scratchpad folders `d142` and `d142v2` of session acb1f403.

## 1. The scope report

### 1.1 How a park ask is built and when it fires

Rota workflow.

- `park_ask` in `rota/core/predicates.py:1522-1561` wakes the Liaison on
  `tick:park_ask` for each `deferred` batch that has a key in
  `given_up(conn, b)` (`rota/core/scheduler.py:1396-1404`, a quarantined
  seat key that names the batch alone). It skips the batch when the item is
  unschedulable (`approval` not `approved`, or `approval_ver < version`),
  when `open_park_ask` finds an open ask, or when a message with the id
  `park_ask_id` already exists. The wake's refs are the item, then the batch.
- `park_ask_id` (`scheduler.py:1415-1439`) is `m_park_` plus ten hex
  characters, `_`, and the batch id. The digest hashes the batch, its head
  commit, its given-up keys and the count of its closed park asks (any status
  other than `open`).
- `park_ask_batch` (`scheduler.py:1442-1446`) reads the batch from the id at
  a fixed offset. `open_park_ask` (`scheduler.py:1449-1455`) finds the open
  one.
- `close_park_asks` (`scheduler.py:1458-1463`) sets the open ask
  `answered`. Its one caller is `db._lift_quarantines`
  (`rota/core/db.py:589-592`), on a write of `batches.head_commit`.
  `close_stale_park_asks` (`scheduler.py:1466-1485`) closes the ask of a
  batch that left the park. `principal.land` closes it on any verdict, a
  contest included (`rota/roles/principal.py:706-710`).
- The consequence of the closed-ask count: any close that leaves the batch
  parked gives a new id, and the predicate fires again. That is by design
  ("a parked batch always has a gate", the predicate's docstring).

Night 132 (observed: `messages`, 2026-10-08): three park asks on bg_2,
`m_park_3b5cf1bd9b_bg_2` (s217), `m_park_34a9fc3543_bg_2` (s240) and
`m_park_5223054458_bg_2` (s269). All three are `answered`. Each was closed by
the walk's `converse`, m117, m140 and m169, and each close made the next id.
The key `liaison|tick:park_ask|confirm_with_default_on_eof,bg_2` reached 3
attempts and was quarantined (copied: `plans/night132-read.md`, section 5,
observed 2026-10-08).

### 1.2 The Liaison's park-ask wake and the answer to it

Rota workflow.

- `rota/roles/prompts/liaison/park_ask.md` tells the Liaison to send one
  `msg.clarify_principal` with the item alone in `refs`, that names the
  batch, the key, "a new commit on the change starts it again" and "a contest
  of the item stops the change", and then asks "a commit that fixes the
  change, or a contest of the item". `park_ask.tools` holds
  `msg.clarify_principal` alone. The call writes one clarify. It moves
  nothing on the batch.
- A person's words go through `parse_reply` (`principal.py:126-144`).
  `words_keep_open` (`principal.py:147-160`) makes a park ask a `reply`, so
  `land` (`principal.py:681-701`) keeps the ask open and writes a principal
  `converse` whose cause is the ask.
- `_mode_key` (`rota/core/runner.py:206-214`) wakes the Liaison in `landing`
  mode on that converse. The payload (`runner.py:1543-1562`) carries the page
  and the note `no_row_to_rule`: "this page is a park ask, and it has no line
  to rule. Words do not move the parked change ... Answer the reply in one
  sentence with `ask`, and name those two ways".
- `rulings.rule` (`rota/roles/api.py:6628-6798`) with `ask=` sends one
  `converse` to the principal with the trigger as its cause
  (`api.py:6668-6680`). With `rulings=` on a park ask it raises "this page is
  a park ask, and it has no line to rule" (`api.py:6681-6691`). So the only
  act the Liaison has on a park-ask answer is a sentence back. No reading of
  the words can land fix, contest or stay.
- The only closes are a head commit (`_lift_quarantines`), a stale close,
  and a verdict through `land`. A person reaches the verdict through
  `rota sign --contest` (commit 0c6e54e2, 2026-09-30). The walk and the agent
  principal have no such route.

Night 132 (observed: `messages` and `turns`, 2026-10-08): the walk's script
answered the park ask with the stock sentence of walk 3 as
`Answer(verb="converse")` (`probes/walk.py:107-118`). `land` took the
verdict path, closed the ask with an empty ruling, and wrote m117. s218 woke
in `landing` mode on m117 and sent `rulings.rule(ask=...)`, m118: "The change
is parked. A new commit starts it again, or a contest of
confirm_with_default_on_eof stops it. Which do you want?".

Night 121, the first shape (copied: `plans/night121-read.md`, section 3,
observed 2026-10-05): s278, s283 and s288 sent `ask=` three times, and s278
first sent eight approvals, which the door refused.

### 1.3 The converse wake and the `recent_chat` block

Rota workflow.

- `rota/roles/prompts/liaison/converse.md` forks on `brief.intake`. A chat
  verdict replies with one `msg.converse_principal(reply=...)`. Both chat
  examples end in a question: `'Hi there! What would you like to build?'`
  and `'Hello! What would you like to build?'`.
- `brief.intake` (`api.py:576-600`) sets `ctx.intake`. The send door in
  `_bind_send.stage` (`rota/core/sandbox.py:2143-2151`) refuses a converse to
  the principal before the claim with "claim the branch first:
  brief.intake(verdict='work') ...".
- `_recent_chat` (`runner.py:1690-1710`) lists up to 8 earlier `converse`
  and `clarify` turns between the principal and the Liaison. It drops every
  row whose `body_text` is empty. The walk and the agent principal write a
  new chat turn as an entry and a message with no `body_text`
  (`probes/walk.py:264-269`, `probes/agent_principal.py:318-324`). So the
  principal's own chat turns never reach `recent_chat`. Only the Liaison's
  replies, and the principal's page replies that `land` wrote with text, do.

Night 132 (observed: the turns of s220, 2026-10-08): s220 was woken by m_p5,
entry e_p5, the stock sentence. Its `recent_chat` held five
`yes that all looks right, go ahead`, the park ask, m118, and the Liaison's
own m119, `The Python version is captured from sys.version_info as
major.minor.micro. Is there anything else I can assist with?`. It did not
hold e_p4, the same sentence one turn before. Turn 1 sent the reply,
refused as `claim the branch first`. Turn 2 called
`brief.intake(verdict='chat')`. Turn 3 sent m119's text again, word for word.
s219 to s227 ran these turns, and 27 such replies ran in the night (copied:
`plans/night132-read.md`, section 5).

### 1.4 `quarantine_looping` and the quarantined wake

Rota workflow.

- `quarantine_looping` (`scheduler.py:1640-1674`) sets an open message
  `quarantined` when `edge_repeats` counts more than `loop_cap` links of the
  same edge on its cause chain. Night 132's m_p13 had 11 links of
  `principal -> liaison : converse` against a cap of 10 (copied:
  `plans/night132-read.md`, section 5).
- `quarantined` (`predicates.py:1458-1519`) wakes the Liaison on
  `tick:quarantined`. Its refs are the `body_refs` of every message in status
  `quarantined`, then each ref of an unreported quarantined tick key that is
  a batch, an item or a ticket. A chat message's refs are its entry, so
  m_p13 gave the ref `e_p13`.
- The tick key is `liaison|tick:quarantined|` plus the refs joined
  (`scheduler.py:1570-1571`). `rota/core/loop.py:331-336` sets `reported = 1`
  on the tick keys after a quarantine wake commits. Nothing marks a
  quarantined message as told, so the wake fires while any quarantined
  message exists, and only the cap of its own key stops it. A new
  quarantined message gives a new key at 0 attempts.
- `rota/roles/prompts/liaison/quarantined.md` asks for one
  `msg.present_principal` that names the stalled work. The page goes through
  `render_page` (`principal.py:346-420`). A batch ref resolves to no row, so
  `touch_words` reads it out as the batch's touch set: the page of a
  quarantine wake on a batch is a touch note.
- What a ruling on that page changes: `land` drops every batch ref from a
  present's `per_item` and returns with nothing when the rest is `approve`
  (`principal.py:719-724`). The ask is already `answered` at that point
  (`principal.py:706-710`). So a `contest` on a batch line closes the page,
  moves nothing, and relays the words to nobody. A ruling on an entry ref
  (`e_p13`) writes no item row, because `UPDATE items ... WHERE id = 'e_p13'`
  matches none, and the relay carries the entry to an owner.
- The brief dates from 2026-08-09 (6afbbad1). Its words were written for
  infrastructure failure, "a model evicted mid-session, a tool call that
  hung". They were never revised for the park of 2026-09-27 and 2026-09-30,
  nor for chat (observed: `git log -- rota/roles/prompts/liaison/quarantined.md`,
  three commits, the last 8ebbae1e on 2026-09-18, which changed the window
  and not this brief's meaning).

Night 132 (copied: frame 142's status of 2026-10-08 08:45 and
`plans/night132-read.md`, section 5): s228, s232 and s236 woke on
`tick:quarantined` for `e_p13`, presented the stock sentence as a page, the
walk approved it, r_9b5d62dac6, r_ab448d074d and r_88cef5cfbd approved
`e_p13`, and relays went to the Vision Keeper, s231, s235 and s239. The keys
grew `e_p13`, then `e_p13,e_p23`, then `e_p13,e_p23,e_p33`. 10 quarantine
wakes ran, the last s290. 9 rulings approved a chat entry, and the sentence
reached decisions `d_d6a6e943fa` and `d_c7c9e325cd`.

Night 133 (observed: `messages` and `rulings`, 2026-10-08): m197 (s313,
`tick:touch_note`, refs `bg_2` and `confirm_default_on_eof`), m199 (s319) and
m201 (s325), both from quarantine wakes with refs `["bg_2"]`. The key behind
them is `developer|tick:tests_failing|bg_2`, 3 attempts, quarantined. The
rulings are r_2e20813fbe `{"confirm_default_on_eof": "approve", "bg_2":
"contest"}`, r_8c0c2918f4 `{"bg_2": "contest"}` and r_32e61cbf06 `{"bg_2":
"contest"}`. All three are `landed` with `verdict_id` NULL: the touch-note
door dropped the batch, and nothing moved. The principal's words, "the
line names the default tests file ... put the new confirm tests with the
other prompt tests", reached no seat.

### 1.5 The walk's scripted principal and the agent principal

Meta workflow.

- `class Principal` (`probes/walk.py:86-118`) answers a `confirm` or a
  `present` with `reply_for`: `WALK_CONTEST` (`regex::words`) contests the
  first numbered line that matches, once a walk, on pages that match
  `WALK_CONTEST_PAGE`; otherwise `WALK_WORDS`. With no `WALK_WORDS` it lands
  a verdict that approves every ref. It answers every other ask, park asks
  included, with the walk's third argument as `Answer(verb="converse")`. It
  has no branch for a park ask.
- The chat path (`probes/walk.py:244-270`) answers every Liaison converse
  with no page under it with the same sentence, as a new entry and message.
  It never reads the cause chain, so the ask-back m118, which sat on the
  park ask, became the new chat turn m_p4.
- `probes/agent_principal.py` labels a park ask "The lead sends you a stopped
  change. Choose a way forward." (`agent_principal.py:211-212`) and lands the
  words through `parse_reply`, so the ask stays open and the Liaison wakes in
  `landing` (`agent_principal.py:226-233`). `chat` follows the cause chain to
  an open ask and lands an ask-back answer there (`agent_principal.py:259-316`).
  `probes/principal_brief.md:27` says to choose one of the named ways and to
  prefer a fix. The agent lands a park answer correctly today. The Liaison
  then has no door that records the choice (copied: `plans/frame41-design.md`,
  section 4a, "a park-ask choice cannot land yet").

### 1.6 The records on these questions

- The park is ruled: "a given-up batch put back in the chair waits for the
  principal ... the principal says what to change or gives up on it, and the
  siblings start meanwhile" (copied: `plans/stack.md:933-942`, ruled: Roman,
  2026-09-27). The grill offered "the team tries again, once" and "not now"
  as the other options, and Roman took the principal option.
- The Liaison writes the park ask, and the scheduler writes no clarify
  (copied: commit b23d17ba, ruled: Roman, 2026-09-30).
- The code reads the 2026-09-27 ruling as "a ruling here would close it and
  cancel the batch on the Liaison's reading" (`api.py:6681-6683`). Roman's
  typed words of 2026-09-27 hold only "Is this about rota or meta? Involve
  the principal?" (observed: `roman_words.py` over the transcripts,
  2026-10-08). So the refusal of a reading is a reading of the ruling, and
  not Roman's words.
- No parser reads a person's words (ruled: 2026-09-10, `parse_reply`'s
  docstring, `principal.py:128-131`). The Liaison reads them and records the
  reading.
- "Nothing is asked twice" (ruled: Roman, 2026-09-12, `rota/DECISIONS.md`,
  "The seat's four pages are one surface", point 1).
- A touch note's lever is a contest of the item: "the owner amends it, the
  version moves, and the revocation is what ends the batch"
  (`principal.py:705-709`, from 8018c376 and f7f2fb93, 2026-09-04). The
  touch-note brief says "the levers are theirs: reorder the work, interrupt
  it, or contest the item".
- "Contest with words goes back to the desk that assumed it"
  (`rota/DECISIONS.md`, the A1 ruling before "The seat's four pages are one
  surface").
- `LAWS.md` and `DECISIONS.md` hold no ruling on a park ask, a chat reply
  that asks a question, or a quarantined chat entry (observed: `grep -n -i
  "park\|chat\|quarantin"`, 2026-10-08). Law 6 says a wake past its cap is
  quarantined and said out loud.

### 1.7 The gate's baseline and the park's gate

- The gate's baseline at adaf2504: `stale (0): none`, and `exit 1: 4 new
  reds, 0 of them flaky`. The 4 reds are
  `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`,
  `L1-CR-fail-names-its-criterion`,
  `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner` and
  `test_map.py::test_mode_lists_its_base_file_and_joins_every_line`. None of
  the 4 is on a site of this frame (copied: the first design's section 3,
  observed from `gate.out` in `d142`, 2026-10-08). Meta workflow.
- Invariant I5 (`rota/tools/invariants.py:167-195`) holds a parked batch to
  exactly one open park ask. `_owes_ask` (`invariants.py:148-164`) says which
  batch owes one: `deferred`, a key in `given_up`, and an item that
  `cancel` would not take, with the NULL rule of `park_ask`. A park that
  closes and stays parked with no new ask is an I5 finding today (observed:
  the code at fb5fbc5f, 2026-10-08). Rota workflow.

## 2. The design

Status: the second design, written by an Opus agent of session acb1f403 on
2026-10-08 after Roman's ruling of 23:25, read-only on the tree at fb5fbc5f.
It replaces the first design's sections 2 to 6. The first design's words
fix, stay and none, its `WALK_PARK` and its chat doors are gone. One
change of the first design stays, with the design review's fix: point D.

Five changes, one per point of the ruling in `rota/DECISIONS.md`, "The
park ask is a page with rows" (ruled: Roman, 2026-10-08 23:25). Point 1 of
the ruling, "there is no fix word", needs no code: the design adds no word.
Rota workflow, except where a line says meta workflow.

The facts of the three nights come from `park_rows.py` and `turns.py` in
the scratchpad folder `d142v2` of session acb1f403 (observed: the night
databases, read with `mode=ro&immutable=1`, 2026-10-08):

| Night | bg_2's criteria | Own tests red at the head | Project tests red |
|---|---|---|---|
| 132 | 6 | 4: cr_1, cr_2, cr_4, cr_5 | 2: `inh_022b8a87`, `inh_51d478df` |
| 133 | 3 | 0 | 2: `tests/test_utils/test_confirm.py`, `tests/test_termui.py` |
| 121 | 6 | 5: cr_1, cr_3, cr_4, cr_5, cr_6 | 2: the same two files |

So night 132 and night 121 get the page, and night 133 gets the note. On
night 121 the own test of cr_1 is `inh_confirm_default_on_eof`, an
inherited test with a `criterion_id`. "Own" means `tests.criterion_id IS
NOT NULL`, and not the id's prefix.

### 2.A The park ask is a page with rows (ruling points 1 and 2)

**The mechanism.** The park ask becomes a `present` whose numbered lines
are the item and its criteria. The page is rendered from rows each time it
is read, as every present is. The principal's rulings land on the lines
through today's door.

1. A new helper, `scheduler.park_reds(conn, batch_id)`, returns two lists:
   the batch's own red tests and its project red tests. It reads the newest
   `test_runs` row per test of the batch, as `failing_attempt` does
   (`rota/core/scheduler.py:1386-1394`), and splits on
   `tests.criterion_id`.
2. A new helper, `scheduler.park_rows(conn, batch_id)`, returns the page's
   refs. When an own test is red, it returns the item, then the batch's
   criteria in id order, from `batch_tickets` joined to `criteria`. When no
   own test is red, it returns `[batch_id]`, the note of 2.B.
3. `park_ask` (`rota/core/predicates.py:1523-1561`) keeps its gate and its
   wake refs, the item and the batch. Its detail gains one word, `page` or
   `note`, from `park_reds`.
4. The send door, `_bind_send.stage` (`rota/core/sandbox.py:1740-1747` and
   `2626-2631`), keys the park on `verb == "present"` in place of
   `"clarify"`. It replaces the session's refs with `park_rows`, whatever
   the session typed, and gives the message the id `park_ask_id`, as today.
   The model chooses nothing on this page.
5. `render_page` (`rota/roles/principal.py:346-506`) gains a keyword
   argument, `ask_id: str | None = None`. When `park_ask_batch(ask_id)`
   names a batch, a park branch runs before the touch-note branch. Four
   callers pass the id: `runner.resolve_inbound` (`runner.py:1547`),
   `api.rulings_rule` (`api.py:6695`), `api.rulings_line` (`api.py:6827`)
   and `principal.pending_asks` (`principal.py:176`). The fifth caller,
   `principal.render_ask` (`principal.py:340-343`), passes no `ask_id`
   (2.F, amendment 8). The numbered order stays the contract with
   `rulings.rule`.
6. The page reads, for night 132's bg_2:

   ```
   This change stopped. The team tried 6 times, and 4 of its 6 checks still fail.
   You asked:
     1. <the item's text>
   It must:
     2. <cr_1's text>
        check: confirm eof default, calls result = confirm("y/n", default_on_eof=True), expects result == True. Fails: assert False == True.
     3. <cr_2's text>
        check: ...
   The last attempt: tests/test_confirm_eof_behavior.py failed: assert False == True.
   Reply 'ok' if every line says what you want. The team then stops here and tells you.
   Name a line to correct only that line. Ask, if something here is unclear.
   ```

   The count comes from `failing_attempt` and `park_reds`. The item is line
   1, because a contest of the item is the one way to stop the change
   (open question 5.1).
7. **The check line is mechanical** (reasoned: the three points below). A
   new helper, `principal.check_line(conn, test_id)`, writes one line from
   the test row: the words of the first `def test_<name>` with `test` and
   the underscores removed; then `calls` and the line of the body that
   assigns the name the first `assert` reads, such as `result = ...`; then
   `expects` and the first `assert` expression; then `Fails:` and the first
   line of the run's output that starts with `E   `, when the newest run is
   red, or `Passes.` when it is green. Every `#` comment is stripped from the
   lines it copies. A test with no run says `Not run yet.` (2.F, amendment
   5: pytest cuts the `FAILED` line's reason to the terminal width, and the
   call is what tells two tests of one criterion apart.)
   - `render_page` renders the page from rows on every read. A line that
     the Liaison writes has no row to live in.
   - The `present` channel has no prose argument. `_bind_send` names that
     argument from the graph (`sandbox.py:2682-2700`), so a written line
     needs a new parameter on every present call and a re-record of every
     present case.
   - The expectation is a fact of the test row. A line that a model writes
     is a second reading between the test and the principal, and the
     principal never rules on a test.
8. **The builder's last attempt is the newest failing run's summary.** It
   is the test's path and the first `E   ` line of the newest red run of
   each own red test at the head commit, at most two lines. The commit
   message is not in a table. No night database holds a `commits` table,
   and the message rides only in a `code.commit` call's `args_summary`
   (observed: `park_rows.py`, nights 121, 132 and 133, 2026-10-08).
9. `rulings.rule` (`rota/roles/api.py:6681-6691`) loses its park refusal.
   The park page is a present, so the door that already exists applies:
   every numbered line takes approve, contest or revise, a contest carries
   the words, and `ask=` sends one sentence back.
10. `land` (`principal.py:648-859`): a park page whose every ruling is
    `approve` writes its verdict message `answered`, so no Liaison session
    wakes on it, and the park rests (2.E). Any other ruling on a park page
    lands as on every present.
11. The landing payload's `no_row_to_rule` note (`runner.py:1548-1562`)
    goes. The page has rows. `words_keep_open` (`principal.py:147-160`)
    and `_mode_key` (`runner.py:209-214`) keep their park clauses, which
    now give the same answer as the present clause.

**The park rests.** `park_ask_id` (`scheduler.py:1415-1439`) counts the
closed park messages of the batch in its digest, so every close gives a
new id and a new ask. That made night 132's three asks. Two things change
(2.F, amendment 2):

- A closed park message that rests does not count. A message rests when it
  is a note (its refs hold the batch), or when its landed ruling names
  `approve` for every ref of the page. The test reads the page's refs, so
  an empty map, such as night 132's three `{}` rulings, never rests.
- The digest gains the sum of the versions of the batch's criteria and of
  its tests. A criterion move or a re-encoded test lifts the park with no
  new head (`db._lift_quarantines`, `db.py:595-612`). The sum then moves,
  the id is new, and a re-park asks again.

So the id stays while nothing moved, the message exists, and `park_ask`
skips the batch. A new head commit, a new key or a version move gives a
new id. `_owes_ask` (`invariants.py:148-164`) returns False for a batch
whose current park id names a closed message that rests, so I5 stays
clean.

**What a contest or a revision of a criterion row does today, step by
step.**

| Step | File and function | Today |
|---|---|---|
| 1. The ruling lands. The `UPDATE items` matches no row, and `verdict:<id>` holds `{criterion: contest}` | `principal.land` | exists |
| 2. The Liaison relays the ruling to the criterion's owner | `prompts/liaison/verdict_signoff.md` says "a criterion has no relay here; leave it" | **one edit**: the brief names `criteria` with `msg.relay_terminologist`, and `RULED_TABLES` (`sandbox.py:814-820`) gains `"criteria": "terminologist"`, so `_owner_of_ref` routes it. `_owner_of_ref` is its one reader |
| 3. The Terminologist reads the ruled words | `_mode_key` gives `relay`, whose tools are `glossary.adopt`, `glossary.lookup` and `ledger.log` | **one edit**: `_mode_key` keys a Terminologist `relay` whose refs hold a criterion to the existing mode `criterion_repair` (2.F, amendment 4) |
| 4. The criterion's version moves | `criteria.respecify` (`api.py:4216-4272`) in `criterion_repair` | exists |
| 5. The park ends | `db._lift_quarantines` (`db.py:595-612`) deletes the batch's quarantined keys and its counts on a criteria move | exists |
| 6. The batch resumes | `tick_batch_start` (`scheduler.py:325-381`) resumes a deferred batch with `_resume_detail` | exists, while `failing_attempt` is below `loop_cap` |
| 7. The Tester rewrites the test from the new words | `criterion_repair` ends with `msg.answer_tester` naming the criterion, and the Tester re-encodes on that message wake | exists: night 121's s311 respecified cr_2 to version 2 and answered the Tester, and s312 re-encoded the test (copied: the design review, 2026-10-08). The brief gains one paragraph for a ruling wake |
| 8. The cancel | `cancel` (`predicates.py:1336-1355`) | not reached. A criterion ruling leaves the item's approval as it is |
| 9. A new batch | `grouping` | not reached. The batch keeps its id and its worktree |

A contest of line 1, the item, takes today's other chain: `land` sets the
item `contested`, `cancel` abandons the batch, `contested` wakes the Vision
Keeper, the amended item goes to the principal again, and `grouping` opens
a new batch on its approval. That chain exists. Night 133 ran it six times
(copied: `plans/night133-read.md`, section 3).

`rota/roles/prompts/terminologist/criterion_repair.md` gains one
paragraph, and its tools do not change:

```
**A ruling of the principal.** When the message is a relay with
`principal_verdict`, the principal read this criterion and its check on a
stopped change, and ruled. The principal's words are the note. For each
criterion with contest or revise, rewrite it with `criteria.respecify` to say
what the words say. Keep the other words of the criterion. Then send
`msg.answer_tester` with the criterion in `refs`, so the Tester encodes the
new words. An approved criterion needs nothing.
```

The existing mode, and not a tool added to `relay`, because a tool in the
list is an invitation (measured: `decisions.author` in a relay mode drew
fourteen decisions a session, 2026-09-03, the comment in `principal.land`).
The existing mode already holds `criteria.respecify` and
`msg.answer_tester`, and its brief already says "Rewrite the criterion to
say what the request says. Keep the other words". Whether the send door
admits `msg.answer_tester` with no Tester question under it is not yet
checked (reasoned: `_answer_evidence`, `sandbox.py:869`, checks only an
answer to a challenge). The implementer proves it on the case of section 3.

**The park-ask brief.** `rota/roles/prompts/liaison/park_ask.md` becomes:

```
MODE: park_ask - the team gave up on a change, and the principal reads it.

The change on the `Refs:` line is parked. The line below the refs names the
batch, what the team gave up on, and `page` or `note`. The other changes go on.

Send one `msg.present_principal`. Put the item and the batch in `refs`. The
door builds the page from the records: the item, its criteria, and what each
check expects and whether it fails. With `note`, the door files a note that
the change stops here. The note asks nothing, and the principal reads it on
the status page.

    msg.present_principal(refs=["<the item>", "<the batch>"])

Do not explain why the team gave up, and do not suggest a fix. Send it once,
then stop.
```

`park_ask.tools` holds `msg.present_principal` alone.

**The two principals.** Meta workflow.

- The walk's scripted `Principal.respond` (`probes/walk.py:86-118`) answers
  every `present` in its first branch: with `WALK_WORDS` set, the words as
  `Answer(verb="reply")`, and the Liaison rules them in `landing`. Without
  them, a verdict that approves every ref, which is the ceiling of 2.E.
  `WALK_CONTEST` can match a criterion line, as it matches any line. No
  change.
- The agent principal (`probes/agent_principal.py:205-234`) labels every
  `present` "The lead sends you a page for your approval." and lands the
  words as a reply. Its park branch, `park_ask_batch(...)` at line 211, is
  not reached, because the present branch comes first. No change. The line
  of `probes/principal_brief.md:27`, "a stopped change ... names the ways
  forward", is no longer cued by a label. It stays, and section 4 says why.

**Tests.**

- Night 132, m117: rebuild bg_2's rows inline (the item, 6 criteria, 6 own
  tests with their bodies' first `assert`, the newest runs, 4 red and 2
  green, the two project reds, and the quarantined key
  `developer|tick:tests_failing|bg_2`). `park_ask` returns one wake with
  the detail word `page`. The door, on a scripted `msg.present_principal`,
  writes a present with the id `park_ask_id` and refs equal to the item and
  the 6 criteria. The page numbers 7 lines, and 4 of them carry `Fails:`.
- Night 132, s218: on s218's trigger, m117 rebuilt as a reply to that page
  with the walk's sentence, `rulings.rule` with 7 approves and the sentence
  as words is admitted. After `apply_rulings`, the page is `answered`, the
  verdict message is `answered`, `park_ask` returns no wake, and I5 finds
  nothing. A ruling `{"3": "contest"}` with the other lines approve lands an
  open verdict whose `verdict:<id>` names cr_2.

### 2.B The page goes to the principal only when a criterion's own test is red (ruling point 3)

**The mechanism.** When `park_reds` finds no own test red, `park_rows`
returns `[batch_id]`, and the park message is a note.

- The note is a `present` that carries the batch's ref, the shape that
  `lifecycle.touch_notes` (`rota/core/lifecycle.py:407-427`) reads as a note
  that waits on nobody (R7).
- The door writes the note closed, with status `answered` (2.F, amendment
  1). `pending_asks` (`principal.py:167-182`) lists every open present, and
  `pump` sends each one to the principal, whose answer wakes the Liaison in
  `landing`. A closed note is never asked, so no answer and no ruling
  exists to drop.
- `render_page`'s park branch, for a note, reads: "This change stops here.
  It breaks checks the project had before: tests/test_termui.py,
  tests/test_utils/test_confirm.py. Nothing waits on you. A new commit on
  the change starts it again." It numbers no line and asks for no reply.
- The note rests, as 2.A says, so `park_ask` asks nothing more.

**Where the batch stays visible.**

- `render_state`'s parked line (`principal.py:279-284`) carries the note's
  text for a batch whose park message is a note: "Stuck: bg_2 stops here.
  It breaks <the project's red test files>. A new commit on the change
  starts it again." The words "I ask you about it next" go for a note,
  because nothing is asked.
- The agenda, `tick_agenda` (`scheduler.py:931-972`), reads open ledger rows
  only. It carries no park today, and the design adds none (reasoned: the
  note and the parked line already show the batch, and a ledger row would
  ask a question that the ruling says is not asked).

**The test.** Night 133, s319's dispatch: rebuild bg_2's rows inline (3
criteria, 3 own tests green at 79870bfc, `inh_022b8a87` and `inh_51d478df`
red, the quarantined key), with bg_2 set `deferred`, the state a park
reaches. bg_2 was `running` at s319, so this sets the one field the park
needs and says so in the test's docstring. `park_reds` gives no own red,
`park_rows` gives `["bg_2"]`, the door writes a present with refs
`["bg_2"]` and status `answered`, `pending_asks` does not hold it, the
parked line names the two files, and `park_ask` then returns no wake.

### 2.C The chat intake for the principal's words goes (ruling point 4)

**The mechanism.**

1. The enum table in `rota/core/sandbox.py:110` keeps `work` alone:
   `("brief", "intake"): {"verdict": ("work",)}`. A call with `chat` is
   refused with: "the principal's words always land on a row. Words about a
   row: `msg.clarify_principal(refs=[<the row>], question=...)`. A question
   about the program: the asks. A request: `verdict='work'`."
2. `brief_intake` (`rota/roles/api.py:576-600`) loses the `chat` entry of
   `nxt`. Its docstring says why.
3. `rota/roles/prompts/liaison/converse.tools` loses
   `msg.converse_principal`. The `answer` mode keeps it, because it carries
   an owner's answer and refs.
4. The intake door in `_bind_send.stage` (`sandbox.py:2141-2190`) loses its
   two `chat` branches. Its `work` branches stay.
5. `brief.segment` refuses a span whose text equals a statement on file
   that is not `superseded`, and names the statement: "these words are
   <s_id>, which is on file. Ask about that row with
   `msg.clarify_principal(refs=['<s_id>'], ...)`." Night 121's s284
   segmented the walk's sentence as s5 a third time.
6. In every Liaison mode that can write to the principal, a send to the
   principal (`msg.clarify_principal`, `msg.converse_principal` in `answer`
   mode, `msg.confirm_principal` and `rulings.rule(ask=...)`) is refused
   when the principal entry on the session's cause chain has the same text
   as an earlier principal entry that already drew a Liaison message: "you
   answered these words in <message id>, and the principal said them again.
   That answer still stands. Stop." The door keys on the entry's text, so
   it holds in `converse`, `answering`, `landing` and `answer` alike (2.F,
   amendment 3). This applies "nothing is asked twice" (ruled: Roman,
   2026-09-12, `rota/DECISIONS.md`, "The seat's four pages are one
   surface", point 1).
7. `_recent_chat` (`rota/core/runner.py:1690-1710`) reads a principal
   message whose `body_text` is empty from the entry in its `body_refs`.

**The converse brief.** `rota/roles/prompts/liaison/converse.md` keeps the
claim, the question route, the work route, the spans and the worked
examples of work and of a question. The chat paragraph and its two
examples are replaced by:

```
**Words that ask for nothing.** A greeting, thanks, a sentence about the program,
an answer to nothing. Every word of the principal lands on a row. Find the row the
words are about: a statement on file, an item, or the open page's line. Send one
`msg.clarify_principal` with that row in `refs`, and ask the one thing the words
leave open about it. When the words are about no row, the row is the entry.

Entry `e_m1` is `hey, morning!`:

    TOOL: msg.clarify_principal(refs=['e_m1'], question='What would you like to build?')

Entry `e_m2` is `remind me, what did we decide about invoice retention?`, and s1 is
`invoices are kept seven years after account closure`:

    TOOL: msg.clarify_principal(refs=['s1'], question='We decided that invoices are kept seven years after account closure. Is that still right?')
```

The first line of the brief changes to "`brief.intake(verdict='work')` if
the message asks for anything at all", with the words about `chat` gone.

**What stays working.** The three `brief.intake(verdict='work')` calls of
night 133, one per request (copied: `plans/night133-read.md`, section 3),
keep working: the enum keeps `work`, the `nxt` sentence for `work` is the
same, and `converse.tools` keeps `brief.segment` and
`msg.confirm_principal`.

**What `recent_chat` shows after the change.** The principal's own turns,
read from their entries; the principal's replies to pages; the Liaison's
questions, marked `asked`; the Liaison's one-sentence answers through
`rulings.rule(ask=...)`; and the `answer` mode's replies that carry an
owner's answer. It holds no chat reply, because no mode writes one.

**The bound on a loop is `loop_cap`** (2.F, amendment 3). A loop through
the principal can still run: a sentence goes to the owners by `msg.ask_*`,
the `answer` mode replies with `msg.converse_principal`, and the walk
answers every Liaison reply with its one sentence. `rulings.rule(ask=...)`
in `answering` also writes a Liaison `converse` with no page under it.
Point 6 stops the second Liaison message on a repeated sentence, and
`quarantine_looping` (`scheduler.py:1640-1674`) stays the bound at
`loop_cap`. The design claims no more than that. A quarantined principal
message can still reach the quarantined wake.

An answer to a clarify on an entry, such as `e_p5`, lands on no row,
because `_table_of_ref` returns None for an entry (copied: the design
review, 2026-10-08). Pass 2's diff review checks what `answering` then does
with it.

**The test.** Night 132, s220: rebuild inline the entry `e_p5` and the
earlier `e_p4` with the walk's sentence, the Liaison's clarify on `e_p4`,
and the inbound m_p5. On s220's turn: `brief.intake(verdict='chat')` is
refused with the sentence of point 1; `msg.converse_principal` is not in
the converse tools; `recent_chat` holds `e_p4`'s text; and
`msg.clarify_principal(refs=['e_p5'], ...)` is refused by point 6. The
same rows with the inbound set as a reply to a clarify, which keys
`answering`, refuse `rulings.rule(ask=...)` on the repeated sentence. A
second case, night 121's s284: `brief.segment` of the walk's sentence,
with s5's row on file as `ratified`, is refused and names s5.

### 2.D The quarantined wake and the batch-line refusal (the first design's 2.3, with the review's fix)

**The mechanism.**

1. A new helper, `scheduler.park_owns(conn, batch_id)`, holds the test that
   `invariants._owes_ask` uses: the batch is `deferred`, `given_up` names a
   key, and the item is schedulable, with `park_ask`'s NULL rule.
   `_owes_ask` becomes `park_owns` and not resting. `park_ask` calls
   `park_owns` too, so the three read one test.
2. In `quarantined` (`predicates.py:1488-1508`), a quarantined tick key that
   is in `given_up(conn, b)` for a batch where `park_owns(conn, b)` holds
   adds no ref, adds no line to `detail`, and does not count in `n`. The
   park page or the note says it. A key of a running batch stays, because
   a running batch has no park (the review's finding: `given_up` reads no
   batch status, and night 133's bg_2 was `running` at s319 and s325).
   The park ask's own key, `liaison|tick:park_ask|<item>,<batch>`, has two
   refs, is never in `given_up`, and still reaches the quarantined wake, so
   law 6 still says it out loud.
3. In `rulings_rule` (`api.py:6629-6798`), after each key maps to a row, a
   `contest` or `revise` on a ref that is a batch is refused, on every
   page: "<batch> is the change's line: a prediction of what it touches,
   and a ruling on it moves nothing. To stop the change, contest the item
   <item>, line <n>. Otherwise approve the line." `land` already drops the
   batch (`principal.py:712-724`), so the refusal changes no landed state.
   It turns a ruling that moves nothing into a choice the Liaison can make.
4. `prompts/liaison/quarantined.md` does not change. The case
   `L1-LI-surface-a-quarantined-message` keeps its prompt.

**The tests.**

- Night 133, s319's dispatch: rebuild inline bg_2 `running`, its item
  `approved` at its version, and `developer|tick:tests_failing|bg_2`
  quarantined with 3 attempts and `reported = 0`. `quarantined` returns one
  wake with refs `("bg_2",)`, because bg_2 was running. With bg_2 set
  `deferred`, the same rows return no wake.
- Night 133, s313's turn: the page m197, refs `["bg_2",
  "confirm_default_on_eof"]`, rebuilt inline. The call that wrote
  r_2e20813fbe, `rulings.rule(rulings={"confirm_default_on_eof":
  "approve", "bg_2": "contest"}, words=<m198's words>)`, is refused, and the
  refusal names `confirm_default_on_eof`. The call
  `{"confirm_default_on_eof": "contest", "bg_2": "approve"}` with the same
  words is admitted.

### 2.E The ceiling: every row approved and a criterion's test still red (ruling point 5)

**The mechanism.** The principal approves every line of a park page, and an
own test is still red at the head commit.

- `land` writes the verdict `answered` (2.A, point 10), so no Liaison
  session wakes. The item stays `approved` at its version.
- The page rests, so `park_ask` writes no second page, and I5 finds
  nothing. The batch stays `deferred` with its key, so `next_batch` skips
  it (`scheduler.py:1379`) and the siblings run.
- `render_state`'s parked line says the team stops: "Stuck: bg_2 stops
  here. You approved its checks as they stand, and 4 of them still fail. A
  new commit on the change starts it again." No new message goes to the
  principal. The approved page is the record, and the parked line is the
  report.
- A commit, a new key, a criterion move or a re-encoded test ends the
  rest, because each moves the digest (2.A, "The park rests"). A bare lift
  of the key with nothing moved keeps the rest. That is the ceiling: the
  principal approved the page, and nothing has changed since.

**What the night read counts.** Two numbers, one line each in the night
read's frame-142 section:

- ceiling pages: park pages (`m_park_` ids, verb `present`, refs without a
  batch) whose landed ruling approves every row while `park_reds` found an
  own test red;
- notes: park pages whose refs hold the batch.

If the ceiling pages pile up, ruling point 5 says the note path of 2.B
grows to cover them. That is a later frame and not this one.

**The test.** Night 121, s278's turn: rebuild bg_2's rows inline (the item,
6 criteria, 6 own tests, 5 red, the two project reds, the quarantined
key). The page numbers 7 lines. s278's first call, a map of eight
approves, is refused: "'8' is not a line of the page". A map of 7 approves
with the walk's sentence is admitted. After `apply_rulings`, the verdict is
`answered`, `park_ask` returns no wake, I5 finds nothing, and the parked
line holds "stops here".

### 2.F Amendments after the design review

The design review on Opus, 2026-10-08, on the tree at fb5fbc5f, found four
high defects and four low ones (observed: `review142v2_findings.md` in the
scratchpad of session acb1f403). Each amendment below takes the review's
fix line. The sentences of 2.A to 2.E and of section 3 that each amendment
touches are already edited, so the record reads as one design. Finding 7
falls away with amendment 4 and has no amendment.

1. **The note is written closed** (finding 1, high). The note of 2.B was
   still a question: `pending_asks` (`principal.py:167-182`) lists every
   open present, `pump` sends it, and the walk and the agent answer a
   present with a reply that wakes `landing`. The door now writes the note
   with status `answered`, so `pump` never asks it. `render_state`'s parked
   line carries the note's text. The words "Reply 'ok'" go from the note.
2. **The park digest moves with the versions** (finding 2, high). A rested
   park did not come back after a criterion move at the same head, which
   is the defect frame 87's review of 4a0ab5c found. The digest of
   `park_ask_id` gains the sum of the versions of the batch's criteria and
   tests. "Approves every row" is defined against the page's refs: the
   landed ruling names `approve` for every ref of the page. An empty map,
   such as night 132's three `{}` rulings, never rests.
3. **The repeated-sentence refusal holds in every mode** (finding 3, high).
   `_mode_key` sends a reply to a clarify to `answering`, and the `answer`
   mode keeps `msg.converse_principal`, so a refusal in `converse` alone
   left the loop open. The refusal now keys on the entry's text in every
   Liaison mode that can write to the principal. The bound on a loop is
   stated as `quarantine_looping` at `loop_cap`, and the design claims no
   more.
4. **The criterion relay goes to `criterion_repair`** (finding 4, high).
   The step after a respecify already exists: night 121's s311 respecified
   cr_2 and sent `msg.answer_tester`, and the Tester's s312 re-encoded the
   test. A Terminologist `relay` whose refs hold a criterion is keyed to
   the existing mode `criterion_repair`, whose brief gains one paragraph for
   a ruling. The session ends with `msg.answer_tester` naming the
   criterion. The new mode `criterion_ruling`, the column
   `tests.criterion_ver` and its five readers are dropped.
5. **The check line is readable** (finding 5, low). `Fails:` comes from the
   first line of the run's output that starts with `E   `, because pytest
   cuts the `FAILED` line to the terminal width (night 132's run `tr248`
   ends `assert F...`). The line adds the call that assigns the asserted
   name, which is what separates cr_1's test from cr_3's. Every `#` comment
   is stripped, as night 121's asserts carry them.
6. **Section 3 gains one case and three tests** (finding 6, low).
   `L3-a-maintainers-question-reaches-the-owner` runs `prompt: converse`
   and is re-recorded. The rewrite of the helper `_liaison_asks` covers
   `test_next_batch.py:231`, `:481` and `:534`.
   `test_the_verdict_vocabulary_is_two_words` is renamed, and its docstring
   rewritten.
7. (Finding 7, the migration of `tests.criterion_ver`: no amendment. The
   column is dropped by amendment 4.)
8. **`render_ask` passes no `ask_id`** (finding 8, low).
   `principal.render_ask` (`principal.py:340-343`) is the fifth caller of
   `render_page`. It renders a page alone for two test files, and it keeps
   its signature.

## 3. The tests and the cassettes

Each test rebuilds its rows inline, as `tests/rota/test_desk_guards.py`
does with `_night_rows`. The night databases are ignored by git. Every
case needs fewer than ten rows of one batch, which `_night_rows` and a few
`INSERT` lines carry. `tests/rota/fixtures/extract_night.py`, as
`test_cycles.py` uses it, suits a cause chain of many messages, and no case
here needs one.

| Point | Case | Real turn | Rows | Kind |
|---|---|---|---|---|
| A | The park ask is a page with the item and the criteria, each with its check | night 132, m117 on `m_park_3b5cf1bd9b_bg_2` | inline | predicate, door, `render_page` |
| A | A full map on the park page lands, and a contest of a criterion line names it | night 132, s218 | inline | sandbox and `apply_rulings` |
| A | A criterion move ends the park, a re-park asks again, and a bare key lift keeps the rest | night 132's bg_2 rows, cr_2 respecified | inline | `_lift_quarantines`, `park_ask_id`, `park_ask` |
| A | The check line takes `Fails:` from the `E   ` line, adds the call and strips comments | night 132, run `tr248`; night 121, `tst_confirm_eof_cr3` | inline | `check_line` |
| B | A park with only project reds is a closed note that `pump` never asks | night 133, s319's dispatch, bg_2 set deferred | inline | predicate, door, `pending_asks`, `render_state` |
| C | The chat verdict is refused, and a repeated sentence is not answered twice in `converse` or `answering` | night 132, s220 | inline | sandbox |
| C | A segment of a statement on file is refused | night 121, s284 | inline | sandbox |
| D | A quarantined key of a running batch still wakes the Liaison | night 133, s319 | inline | predicate |
| D | A contest on a batch line is refused with the item named | night 133, s313, r_2e20813fbe | inline | sandbox |
| E | A whole approve on a park page rests the park | night 121, s278 | inline | sandbox, `apply_rulings`, I5 |

**Recorded cases whose prompts change** (observed: the `prompt:` and
`tick:` keys and the inbound verbs of `tests/rota/cases/*.yaml`, and a text
search of `tests/rota/cassettes.db`, which holds 5 prompt hashes with
`MODE: park_ask`, 120 with `MODE: converse` and 31 with `MODE:
verdict_signoff`, 2026-10-08):

- `L1-LI-a-parked-batch-is-put-to-the-principal-once`
  (`l1_liaison2.yaml:384`): the brief, the tools and the expectation
  change. The fixture gains criteria, tests and runs. The expectation
  becomes one `present` with `refs_equal` the item and the criteria.
  Rewrite, then record 5 runs.
- One new case beside it, the note: the same fixture with only project
  tests red, one `present` with `refs_equal: [<b1>]`. Record 5 runs.
- `L1-LI-chat-is-not-work` (`l1_liaison.yaml`, first case): its
  expectation, a `converse` to the principal, becomes one `clarify` with
  `refs_include: [e_<m_in>]`. Rewrite, then record 5 runs.
- `L1-LI-segment` and `L1-LI-no-report-no-question` (`l1_liaison.yaml`),
  `L1-LI-a-question-about-the-program-goes-to-its-owners`
  (`l1_liaison2.yaml:280`), `G1-scope-sounding-words-are-not-scope-yet`,
  `G1-what-the-brief-already-holds-is-answered-from-it` and
  `G1-a-reply-that-answers-something-else-ratifies-nothing`
  (`g1_segments.yaml`): `converse.md` and `converse.tools` change. Their
  expectations hold (reasoned: the G1 retention case expects a message to
  the principal with `refs_include: [<s1>]` and names no verb). Re-record.
- `L3-a-maintainers-question-reaches-the-owner`
  (`l3_handoffs.yaml:213`): its first step runs `prompt: converse`.
  Re-record (2.F, amendment 6).
- `L1-LI-relay-a-ruling-without-interpreting-it` and
  `L1-LI-a-ruling-splits-by-owner` (`l1_liaison2.yaml:68`, `:316`):
  `verdict_signoff.md` changes. Re-record.
- `L1-TE-repair-the-criterion-the-tester-cannot-encode`
  (`l1_unresolved.yaml`, `tick: criterion_repair`): `criterion_repair.md`
  gains a paragraph. Re-record.
- One new case, `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told`,
  in `l1_terminologist.yaml`: a relay of `{cr_2: "contest"}` with night
  132's criterion and words, in mode `criterion_repair`. It expects one
  `criteria` write on cr_2 and one `answer` to the Tester with cr_2 in its
  refs. Record 5 runs.
- No change: the 7 `l1_landing.yaml` cases (the `no_row_to_rule` note
  rode on park pages alone), `L1-LI-surface-a-quarantined-message`, the 2
  Terminologist `relay` cases (their mode does not change), and the 7
  `tests_missing` cases. The gate's stale line after each pass decides, and
  the agent re-records what it names.

**Unit tests that assert the old words.** The agent rewrites them to the
new page and keeps their intent:

- `tests/rota/test_next_batch.py`: the park sentence at lines 202-203, and
  `test_a_words_answer_leaves_the_park_ask_open_and_wakes_landing_once`
  (286), `test_a_contest_after_a_words_answer_still_abandons_the_batch`
  (335), `test_the_parked_line_names_only_what_the_principal_can_do` (378),
  `test_a_re_park_after_a_commit_asks_again_in_the_same_words` (414),
  `test_a_lift_with_no_head_change_asks_again_on_the_re_park` (431),
  `test_an_approve_then_a_lift_with_no_head_change_asks_again` (458) and
  `test_a_contest_on_the_park_ask_abandons_the_batch` (497). Test 458
  lifts by deleting the key, with nothing moved. Under the rest rule that
  lift keeps the rest, so the test lifts by a criterion move to keep its
  intent, and a second assertion pins that a bare lift asks nothing.
- The helper `_liaison_asks` in `test_next_batch.py` scripts
  `msg.clarify_principal` with `_PARK_QUESTION`, which the new
  `park_ask.tools` refuses. The helper's rewrite to `msg.present_principal`
  covers three more tests that call it:
  `test_a_quarantined_batch_resumed_after_a_preempt_waits_for_the_principal`
  (231), `test_a_park_ask_does_not_hide_a_contradiction` (481) and
  `test_a_hand_commit_found_at_boot_ends_a_quarantine_park` (534).
- `tests/rota/test_intake_fork.py::test_chat_claimed_means_a_bare_reply_is_legal`
  (line 75) inverts: `chat` is refused.
  `test_the_verdict_vocabulary_is_two_words` (line 82) keeps passing, but
  its name and docstring are no longer true. Rename it to
  `test_the_verdict_vocabulary_is_work_alone` and rewrite its docstring.
- Files that name `park_ask`, `no_row_to_rule` or the `chat` verdict, which
  the agent reads for the old words: `test_t0_sandbox.py` (13 lines),
  `test_scene_two_batches.py` (3), `test_scene_park.py` (2),
  `test_invariants.py` (2), `test_agent_principal.py`,
  `test_desk_guards.py`, `test_predicates.py` and `test_roles_doc.py` (1
  each), and `rota/testkit/scenes.py:569`, whose `PARK_ASK` script sends a
  clarify.

## 4. What the design does not change, and why

- The park's gate stays: `park_ask` fires on the same batches, the Liaison
  writes the message (ruled: Roman, 2026-09-30, commit b23d17ba), and the
  scheduler writes none.
- The touch note stays a sense check with no gate. Only a ruling on a batch
  line is refused, and the lever stays the item's.
- `quarantine_looping` and `loop_cap` stay. They stopped night 132's loop,
  and they stay the bound on a loop through the principal. 2.C's point 6
  stops a repeated sentence from drawing a second Liaison message, and
  claims no more.
- A quarantined message that stays quarantined still wakes the Liaison
  until its key reaches the cap. Night 133 had 7 such single presents. That
  is a separate wall if a night shows it.
- `rota sign --contest` and the commit exit stay. A person can still commit
  on the branch, and `_lift_quarantines` ends the park.
- `rulings.rule(ask=...)` stays one sentence per session on an open page.
  The park page now has rows, so the reason for night 121's three asks, a
  page with no line to rule, is gone. The ends-when ratio, at most 1 park
  ask in 4 asked more than once, measures the rest.
- The agent principal and `probes/principal_brief.md` stay. Line 27 names
  "a stopped change", and the park page says "This change stopped", so the
  line can still steer a model. It tells the model to "choose one of those
  ways", and the page names none, so the model reads the lines. The night
  read checks the agent's park answers. Meta workflow.
- `landing.md` stays. A park page is a present, and the landing brief
  already rules a present's lines.
- Frame 184, the ask-back copied from `recent_chat`, and frame 185, the
  `separate request` word, are not this frame. 2.C changes what
  `recent_chat` holds, so frame 184's interview runs on the new block.

## 5. The open questions

Each was checked against the records first (section 1.6 and the ruling of
2026-10-08). The records answer three questions that the design met, and
those are not asked:

- Whether a contest on a batch line goes to the Architect: no. The records
  give a batch-line contest no meaning, and the lever is the item's
  (`principal.land`, 2026-09-04, and the touch-note brief).
- Whether the ceiling writes a new message: no. Ruling point 5 says the
  team reports that it stops, and point 3 says a note asks nothing. The
  parked line reports it, and the approved page is the record.
- Whether a project-only red asks the principal anything: no. Ruling point
  3 says a note with no question, and the Developer owns a project test's
  red (ruled: 2026-09-14).

Two questions stay open:

1. **[med] Is the item line 1 of the park page?** The records: ruling point
   2 says "the rows are the item's criteria". The touch note and the old
   park ask both name a contest of the item as the way to stop a change
   (`principal.land`, 2026-09-04, and the first park ask of 2026-09-30).
   Without the item on the page, the principal can stop a change only by
   contesting every criterion, which moves the version and starts the
   Tester again. Recommended: yes, the item is line 1, under "You asked:".
   An approve of line 1 changes nothing, because the item is already
   approved at its version.
2. **[low] Does the mechanical check line read well enough for a person?**
   The records: none on this line. On night 132 a line reads "confirm eof
   default, calls result = confirm("y/n", default_on_eof=True), expects
   result == True. Fails: assert False == True." (observed: the body of
   `tst_confirm_eof_default` and the `E   ` line of its newest run,
   2026-10-08).
   Recommended: ship the mechanical line, and count in the next night read
   how many park answers ask what a check means. If the count is above 1
   in 4, a later frame has the Tester write the line at encode, on the
   `tests` row.

## 6. Price

The design is two passes, each with its own implementer pass and its own
diff review on Opus. The prices come from the design review's line: one
pass for the whole design would cost 250k to 300k, on the anchor of 216.9k
for a cold pass of 18 files, 666 insertions and 11 tests (frame 66,
`plans/operating-facts.md`). A cap in a brief does not bind.

**Pass 1, the park page: 2.A, 2.B, 2.D and 2.E.** About 200k for the
implementer pass and about 120k for its diff review. Pass 1 lands first,
because 2.B and 2.E rest on 2.A's helpers and 2.D's `park_owns`.

- Files: `rota/core/scheduler.py` (`park_reds`, `park_rows`, `park_owns`,
  `park_ask_id`), `rota/core/predicates.py` (`park_ask`, `quarantined`),
  `rota/core/sandbox.py` (the park door, `RULED_TABLES`),
  `rota/roles/principal.py` (`render_page`, `check_line`, `land`,
  `render_state`, `pending_asks`), `rota/roles/api.py` (`rulings_rule`,
  `rulings_line`), `rota/core/runner.py` (`resolve_inbound`, `_mode_key`),
  `rota/tools/invariants.py` (`_owes_ask`),
  `rota/roles/prompts/liaison/park_ask.md` and `.tools`,
  `rota/roles/prompts/liaison/verdict_signoff.md`,
  `rota/roles/prompts/terminologist/criterion_repair.md`,
  `rota/testkit/scenes.py`, and the tests of points A, B, D and E in
  section 3, with the rewrites in `test_next_batch.py` and the park lines of
  the other test files.
- Re-records, GPU apart: the rewritten park case and the new note case at 5
  runs each, the 2 `verdict_signoff` cases, `L1-TE-repair-the-criterion-the-tester-cannot-encode`,
  and the new Terminologist case at 5 runs.

**Pass 2, the chat intake: 2.C.** The rest of the design's price: about
80k for the implementer pass, on the anchor of 77k for one tool of 340
lines with 20 tests and a gate run (frame 24), and about 80k for its diff
review, on four points.

- Files: `rota/core/sandbox.py` (the enum, the intake door, the
  repeated-sentence refusal in every mode that writes to the principal),
  `rota/roles/api.py` (`brief_intake`, `brief.segment`, `rulings_rule`'s
  `ask=` path), `rota/core/runner.py` (`_recent_chat`),
  `rota/roles/prompts/liaison/converse.md` and `.tools`, and the tests of
  point C in section 3 with the `test_intake_fork.py` rewrites.
- Re-records, GPU apart: `L1-LI-chat-is-not-work` rewritten at 5 runs, and
  the 7 converse cases of section 3, `L3-a-maintainers-question-reaches-the-owner`
  included, on their old expectations.

One night after both passes, apart, to read the three ratios of the
ends-when. The frame's old line, about 70k, priced the first design and is
too low for this one.
