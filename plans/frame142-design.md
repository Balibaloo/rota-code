# Frame 142, a park ask gets an answer that names no option: the scope and the design

Status: written by an Opus agent of session acb1f403 on 2026-10-08, before any
code, read-only on the tree at adaf2504. Both workflows. Each line names its
workflow where the two differ. The night facts come from
`.rota/clickI_night132.db`, `.rota/clickI_night133.db` and
`.rota/clickI_night121.db`, read with `mode=ro&immutable=1` by the scripts
`q.py` and `roman_words.py` in the scratchpad folder `d142` of session
acb1f403.

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

## 2. The design

Four changes, one per site. A change that touches a brief puts the new words
in the payload where it can, so the recorded prompts of other cases stay as
they are (the pattern of `no_row_to_rule`, `runner.py:1554-1557`).

### 2.1 The walk's scripted principal answers a park ask with one option

Meta workflow.

- Mechanism: a new importable module, `probes/walk_park.py`, holds
  `park_answer(rendered: str, spec: str) -> str`. `walk.py` runs on import
  and cannot be tested, so the rule lives beside it. `spec` comes from
  `WALK_PARK`: one option word, `fix`, `contest` or `stay`, or a list
  `regex::option;regex::option` matched against the rendered page in order,
  the first match winning, with the last plain word as the fallback. The
  default is `stay` (open question 5.3). The words are fixed per option, in
  a person's words:
  - `fix`: "Fix it and try again."
  - `contest`: "Stop this change. I do not want it as it is."
  - `stay`: "Leave it parked for now."
- `Principal.respond` gains a branch before the clarify path: when
  `park_ask_batch(ask.message_id)` is set, it answers once with
  `Answer(verb="reply", text=park_answer(ask.rendered, WALK_PARK))`, so
  `land` keeps the ask open and the Liaison reads it in `landing`. The log
  line keeps its shape: `[<id>] park: <head>  -> '<words>'`.
- The chat path follows the cause chain as the agent does: a Liaison
  converse whose chain reaches an open principal ask is answered once on that
  ask with `parse_reply`, through `land`. A Liaison chat turn with no page
  under it is answered with the sentence once a walk. A second such turn is
  marked `answered` and writes no entry, the agent's `(nothing)` (copied:
  `plans/frame41-design.md`, "A chat turn with no question under it: say that
  nothing else is needed, once").
- The agent principal needs no change. It labels the page, lands the words
  through `parse_reply`, and its brief tells it to choose a named way. The
  park page's words change in 2.2 from two ways to three, and the brief's
  "choose one of those ways" covers three.
- Test: `tests/rota/test_walk_park.py` renders night 132's
  `m_park_3b5cf1bd9b_bg_2` from its row and checks that `park_answer` gives
  each option's words for `fix`, `contest`, `stay`, and for a regex list,
  and that the scripted answer is a `reply` and not a `converse`. The real
  turn is the walk's m117, which closed that ask as a `converse`.

### 2.2 The Liaison's intake of a park-ask answer lands the option it names

Rota workflow.

- The door is a ruling word that the Liaison writes, never a word match. A
  word match is the keyword layer that the ruling of 2026-09-10 removed. The
  Liaison reads the reply and calls `rulings.rule` with the item as the one
  key and one of four words as the value: `fix`, `contest`, `stay` or
  `none`, with the reply whole as `words`.

      rulings.rule(rulings={"<the item>": "<fix|contest|stay|none>"}, words="<the reply, whole>")

- The door in `rulings_rule` (`api.py:6681-6691`), on a page where
  `park_ask_batch(page["id"])` is set: the map has exactly one key, the item
  on the page's refs. The value is one of the four words. `words` equals the
  trigger's text after whitespace is joined, so the record carries the
  person's own words and not the Liaison's summary. This check is mechanical,
  and it is how the door keeps "the principal decides" (section 1.6). The
  four words are refused on any other page, with today's sentence, "is not
  a ruling. Each line takes approve, contest or revise". `ask=` stays as it
  is, for a reply that asks about the page.
- The signature and the docstring of `rulings.rule` do not change. The new
  words go in the payload: `no_row_to_rule` (`runner.py:1558-1562`) is
  replaced by `park_choice`, two sentences and the call above. The sentences:
  "This page is a park ask. Read which way the reply names: `fix` (the team
  tries again with these words), `contest` (the change stops), `stay` (the
  change stays parked), or `none` when it names none of the three. A `none`
  sends nothing back: do not ask again." So the 7 recorded landing cases keep
  their prompts.
- What each word does in the tables, in `land` (`principal.py:648`), behind a
  new branch for a park ask whose `per_item` holds one of the four:
  - `contest`: today's verdict path, unchanged. The ask is `answered`, the
    item goes `contested` at its version, the relay carries the words to the
    item's owner, and `cancel` abandons the batch. A person's
    `rota sign --contest` already takes this path.
  - `fix`: the ask is `answered`. The batch's seat keys in
    `given_up(conn, batch)` are deleted from `tick_attempts`, and
    `_forget_batch_counts(conn, batch, keep=("%|tick:tests_missing|%",
    "%|do:park|%"))` runs, the same lift a criterion move makes
    (`db.py:600-611`). The batch is `deferred` and no longer `parked`, so
    `next_batch` resumes it. The ruling row keeps the words, and the
    Developer's next wake on the batch carries them as `principal_said`,
    the key that a relay's payload already uses (`runner.py:1350-1352`).
    Where the Developer's batch wake is built is not read here (reasoned:
    the implementer finds it with `python -m rota.tools.map`). The bound is
    open question 5.1.
  - `stay`: the ask is `answered`, and the batch stays parked. Its siblings
    run, as today. `park_ask_id` counts the closed asks without the asks
    closed by `stay` or `none`, so the same head and keys give the id that
    exists, and the predicate does not fire again until the head or the keys
    move.
  - `none`: the ask stays `open`. `land` returns no verdict, and
    `apply_rulings` (`principal.py:862-893`) marks the ruling `landed` and
    not `stale`, because a `none` is a reading that landed. The landing wake
    drains on the commit, `park_ask` skips the batch because
    `open_park_ask` finds the ask, and the Liaison sends nothing. A later
    answer on the same open page wakes `landing` again and can name an
    option. The ask does not fire again on the `none` answer.
- `park_ask.md` names three ways and drops "a commit that fixes the change":
  a fix, where the team tries again with what the principal says; a contest
  of the item, which stops the change; or leave it parked. `render_state`'s
  parked line (`principal.py:279-290`) says the same three ways.
- Tests, `tests/rota/test_park_choice.py`, on night 132's rows at s218, the
  park ask `m_park_3b5cf1bd9b_bg_2` and the reply m117 rebuilt as a
  `reply`:
  1. s218's reply, the stock sentence, with `{item: "none"}`: admitted, the
     ruling lands, the ask stays `open`, and `park_ask` returns no wake.
  2. `fix`, `contest` and `stay` on the same rows with the 2.1 words: the
     table states above, one assertion each.
  3. `{item: "approve"}`, a two-key map, a key that is not the item, and
     `words` that differ from the reply: each refused with its sentence.
  4. `fix` on a page that is not a park ask: refused with today's sentence.
  5. Night 121's s278 call shape, eight approvals on the park page: refused,
     and the refusal names the call above.

### 2.3 A contest on a quarantined wake's page moves something

Rota workflow. The history supports the second way the brief names: the
quarantined wake does not present a batch that the park owns, and the park
ask asks the question. The reasons, from section 1.6: the quarantined brief
was written in 2026-08 for infrastructure failure and was never revised for
the park, and the park design of 2026-09-27 and 2026-09-30 made the park ask
the one gate of a given-up batch ("a batch with a quarantined key reaches
the page through one message only", commit 0c6e54e2). The records hold no
meaning for a `contest` on a batch. Their meaning is a contest of the item.

- Mechanism, in `quarantined` (`predicates.py:1501-1508`): a quarantined tick
  key that is in `given_up(conn, b)` for its batch adds no ref, adds no line
  to `detail`, and does not count in `n`. Those keys belong to `park_ask`
  when the item is schedulable, and to `cancel` when it is not. The park
  ask's own key, `liaison|tick:park_ask|<item>,<batch>`, has two refs, is
  not in `given_up`, and still reaches the quarantined wake. That keeps law
  6's "said out loud" when the park ask itself gives up.
- Second door, in `rulings_rule`, for every page: `contest` or `revise` on a
  batch ref is refused, "the batch's line is a prediction of what it
  touches, and a ruling on it moves nothing. To stop the change, contest the
  item <item>. Otherwise approve the line". `land` already drops the batch,
  so the refusal changes no landed state. It turns a silent no-op into a
  choice the Liaison can make. Open question 5.2 asks whether a batch-line
  contest should instead go to the Architect.
- No brief changes, so `L1-LI-surface-a-quarantined-message` keeps its
  prompt. Its refs are an item.
- Tests: on night 133's rows at s319's dispatch, `quarantined` returns no
  wake on `bg_2` while `developer|tick:tests_failing|bg_2` is its only
  quarantined key. On s313's turn, the call that wrote r_2e20813fbe,
  `{"confirm_default_on_eof": "approve", "bg_2": "contest"}` with m198's
  words is refused with the item named, and
  `{"confirm_default_on_eof": "contest"}` with the same words is admitted.

### 2.4 The chat loop

Rota workflow.

- `recent_chat` holds the principal's chat turns. `_recent_chat`
  (`runner.py:1690-1710`) reads the entry text for a principal `converse`
  whose `body_text` is empty and whose refs name an entry, and marks the
  current entry's text `"said_before": true` when an earlier principal turn
  in the list holds the same text after whitespace and case are joined. The
  brief does not change.
- The door, in `_bind_send.stage` (`sandbox.py:2143-2175`), after the intake
  checks: on a converse to the principal with `ctx.intake == "chat"`, when
  the trigger's entry text is marked `said_before`, a reply that holds a
  question mark is refused: "they said this before, and your reply to it is
  in `recent_chat`. Reply in one sentence with no question, or end the
  session with no call." The walk then has no question to answer, and a
  person who repeats themselves gets a statement.
- The work branch of the same loop, night 121's shape: `brief.segment`
  (`api.py:603`) refuses a statement whose text equals a `ratified`
  statement's text after whitespace and case are joined, "statement <id>
  already holds these words and is ratified. Use its id". Frame 142's
  ends-when names this part (`plans/stack.md`, frame 142, the ends-when).
- A quarantined chat entry is not presented: `quarantined`
  (`predicates.py:1482-1488`) skips a quarantined message whose `from_role`
  is `principal` and whose refs are entries alone. A principal's chat turn
  is not work that left the system, which is what the brief says the wake is
  for. The skip also removes night 132's growing key, because no chat entry
  joins the refs.
- Tests:
  1. s220's turn 3 call, night 132:
     `msg.converse_principal(refs=["e_p5"], reply="The Python version is
     captured ... Is there anything else I can assist with?")` after
     `brief.intake(verdict='chat')`, on night 132's rows at s220: refused.
     The same reply with no question mark: admitted.
  2. `_recent_chat` on night 132's rows for m_p5 holds e_p4's text with
     `from: principal`, and the current entry is `said_before`.
  3. `quarantined` on night 132's rows at s228's dispatch returns no wake on
     `e_p13`.
  4. Night 121's s284 `brief.segment` of the stock sentence, with s4
     ratified: refused, and the sentence names s4.

## 3. The tests and the cassettes

| Case | Real turn | Kind | Cassette |
|---|---|---|---|
| The walk answers a park ask with one option | night 132, m117 on `m_park_3b5cf1bd9b_bg_2` | unit, `probes/walk_park.py` | none |
| A reply that names no option clears the wake as no choice | night 132, s218 | sandbox on rows | none |
| An answer that names an option lands it, fix, contest, stay | night 132, s218's rows, with 2.1's words | sandbox and `land` | none |
| A ruling on a park page refuses the old shapes | night 121, s278 | sandbox | none |
| A quarantined batch key that the park owns wakes no present | night 133, s319 | predicate on rows | none |
| A contest on a batch line is refused with the item named | night 133, s313, r_2e20813fbe | sandbox | none |
| A chat reply to a repeated sentence asks no question | night 132, s220, turn 3 | sandbox | none |
| A quarantined chat entry is not presented | night 132, s228 | predicate on rows | none |
| An equal statement is refused at segment | night 121, s284 | sandbox | none |
| The Liaison records `none` on a park page | night 132, s218's prompt | new L1 case, `l1_landing.yaml` | record 5 runs |
| The Liaison records `fix` on a park page | s218's page with "Fix it and try again." | new L1 case | record 5 runs |

Stale by the change (reasoned: which prompts the change moves):

- `L1-LI-a-parked-batch-is-put-to-the-principal-once`: `park_ask.md`
  changes. Re-record 5 runs. Its expectations, refs equal to the item and
  words that name the batch and the key, still hold.
- The 7 `l1_landing.yaml` cases: none, because the park words ride in the
  payload of a park page only, and the signature and docstring of
  `rulings.rule` do not change.
- The converse cases (`L1-LI-chat-is-not-work`, `L1-LI-segment`,
  `L1-LI-no-report-no-question`, three `G1` cases): stale only if a fixture
  holds a principal converse with no `body_text` beside an entry. The gate's
  stale line after the pass decides. Re-record those it names.
- `L1-LI-surface-a-quarantined-message`: none. Its refs are an item.

The stale lines were not read, because the gate was still running when this
record was written (observed: `python -m rota.tools.gate` started 19:44 on
2026-10-08, no output at the time of writing). The list above comes from the
test files alone (reasoned). The cassette the re-records and the new cases
touch is `tests/rota/cassettes.db`. The case files are
`tests/rota/cases/l1_liaison2.yaml` (the park-ask case) and
`tests/rota/cases/l1_landing.yaml` (the 2 new cases). The converse cases in
`tests/rota/cases/l1_liaison.yaml` and `tests/rota/cases/g1_segments.yaml`
are stale only if the gate after the pass names them. The sandbox, unit and
predicate tests replay database rows and need no cassette.

## 4. What the design does not change, and why

- The touch note stays a sense check with no gate. Only the batch-line
  ruling is refused. The levers stay the item's.
- The quarantined message's own bound stays as it is: nothing marks a
  quarantined message as told, and the wake's key is its refs. With chat
  entries and park-owned keys out of the refs, no observed night grows a key.
  A message that stays quarantined still wakes the Liaison until its key
  reaches the cap, and that was 7 single presents on night 133. That is a
  separate wall if a night shows it.
- `quarantine_looping` and `loop_cap` stay. They stopped night 132's loop at
  11 links, and this design removes the loop before the cap.
- The `converse.md` examples stay. The 2026-09 tuning of the chat fork
  measured the greeting regression on those examples (`rota/DECISIONS.md`,
  the chat-or-work rulings), and a door on the repeat case costs no
  re-record of them.
- `rota sign --contest` and the commit exit stay. A person can still commit
  on the branch, and `_lift_quarantines` closes the ask.
- Frame 184, the ask-back copied from `recent_chat`, and frame 185, the
  `separate request` word, are not this frame. 2.4 changes what
  `recent_chat` holds, so frame 184's interview runs on the new block.
- The agent principal and its brief stay.

## 5. The open questions

Each was checked against the records first, section 1.6.

1. **[high] How many times can the principal choose `fix` on one batch?** The
   records: Roman took "waits for the principal" over "the team tries again,
   once" on 2026-09-27, and said "the principal says what to change". No
   record bounds a fix that the principal chose. Without a bound, the agent
   principal, which prefers a fix, can park, fix and park a batch for a
   whole walk, at about three Developer attempts a round. Recommended: one
   `fix` per batch. The second park ask of that batch names only `contest`
   and `stay`, and the door refuses `fix` with that sentence.
2. **[med] Should a contest on a batch line go to the Architect, who made
   the touch prediction, instead of being refused?** The records: "contest
   with words goes back to the desk that assumed it", and the touch-note
   brief and `land` name the item as the lever. Night 133's words were about
   which test file the confirm tests go in, which is the Tester's and the
   criteria's ground, not the touch. Recommended: refuse now, as 2.3 says,
   and count batch-line contests in the next two night reads before a route
   is built.
3. **[low] What does the scripted walk answer by default when `WALK_PARK` is
   unset?** The records: none. Recommended: `stay`, because it ends the park
   ask with no new Developer work and the siblings run. The gauntlet sets
   `WALK_PARK=fix` on a night that measures the fix path.
4. **[med] Does the reading of the park choice by the Liaison keep the
   ruling of 2026-09-27?** The records: the code says a reading would cancel
   "on the Liaison's reading", and Roman's typed words say "involve the
   principal". The design keeps the person's words whole on the ruling row,
   checked by the door, and the Liaison writes only which named option the
   words choose. Recommended: yes, it keeps the ruling, because every other
   page already lands on the Liaison's reading of the person's words
   (`parse_reply`, ruled 2026-09-10).

## 6. Price

One implementer pass on Opus, about 70k, since the change touches the
landing door, `land`, two predicates, the send door, `_recent_chat`, one
brief, the walk and a new module. One diff review of about 70k. One re-record
of 1 case at 5 runs and 2 new L1 cases at 5 runs each, GPU apart. One night
with `WALK_PARK=fix`, apart.
