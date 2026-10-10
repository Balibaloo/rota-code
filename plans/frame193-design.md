# Frame 193, the second request: the scope and the design

Status: written by an Opus agent of session 45fc3fe2 on 2026-10-10 at
about 04:09, before any code, read-only on the tree at 43461f47. The code
of the tree differs from night 137's tree af535499 in three commits only,
fe9f14b6, 5ffa1244 and afecf14a, which touch `disputed_paths` in
`rota/core/runner.py` and the capture in `rota/testkit/fixtures.py`
(observed: `git diff --stat af535499 HEAD -- rota tests probes`,
2026-10-10). No site of this design is in those commits. The night facts
come from `.rota/clickI_night137.db` with its `-wal`, opened with
`mode=ro`, and `.rota/clickI_night133.db`, opened with
`mode=ro&immutable=1`, by inline scripts of this agent (observed:
2026-10-10). No model call was made. Rota workflow, except where a line
says meta workflow.

Verdicts, one line each:

- The principal saw walk 2's page m161 after walk 3's request m_p3,
  because `pending_asks` lists every open ask by `seq`, and nothing closes
  a page when a request lands. The walk inserts m_p3 and calls
  `pending_asks` before any session runs. Section 1.1.
- m186 came from the `quarantined` predicate on the key
  `vision_keeper|tick:contested|confirm_with_default_on_eof`, which the
  `contested` predicate earned after s299's ruling. The send door stamped
  the confirm criteria, because `request_rows` stamps what the refs reach.
  Section 1.1.
- s299's and s314's words reached the confirm item through `land`, which
  writes `contested` on every ruled item, and through the relay split,
  which sent the five criteria to the Terminologist in `criterion_repair`,
  where s316 respecified them. Section 1.2.
- `grouping` reads no item approval and no version. `tick_slicing`,
  `next_batch` and `cancel` read both. So the grouping opens a batch that
  the cancel abandons in the same pass. Section 1.3.
- A park today is a batch state, a deferred batch the team gave up on. No
  item can be parked, by the system or by the principal, and nothing can
  reopen one. Section 1.4.
- s293, s295 and s297 asked which lines relate, because the `landing`
  brief says to ask when "you cannot tell which lines the reply is about",
  and every line of m161 was the confirm request. Section 1.5.
- Five changes, section 2: the request boundary, the park of an earlier
  request's item, one request per page, the grouping guard, and the words
  door.

## 1. The scope report

### 1.1 Which predicate presented m161 and m186 after walk 3's request

**How the request entered** (observed: `probes/walk.py` lines 39 to 52,
2026-10-10). Each walk is a new process. When its sentence is not the last
principal entry, the walk inserts the entry `e_p<n>` and a message `m_p<n>`
with no `cause_id`, verb `converse`, from `principal` to `liaison`. Then the
loop starts. The first thing each step does is
`pending_asks(conn)` (`probes/walk.py` line 233). The TUI path does the
same through `talk.open_with` (`rota/tools/talk.py:55-87`): an entry and an
uncaused `converse`. So a request is a principal `converse` with no
`cause_id` (observed: night 137, m_p3 has `cause_id` NULL; every answer to
a page has the page as its cause, 2026-10-10).

**The order on night 137** (observed: `messages`, night 137, 2026-10-10):

| seq | Message | What |
|---|---|---|
| 163 | m161 | walk 2's agenda page, sent by s290 on `tick:agenda`, refs the 7 ledger rows, the confirm item and its 5 criteria |
| 164 | m162 | walk 2's answer to m161. s291 sent `ask` as a ruling word, was refused twice, and ended. m161 stayed open |
| 165 | m_p3 | walk 3's request, `["e_p3"]`, no cause |
| 166 | m163 | the agent principal's answer to m161: "Line 1 is the wrong change ... the change I'm working on now is the show_python flag" |
| 167 | m164 | s292's confirm of s3, sent after m163 |

So the principal answered m161 before any rota session read m_p3.

**The predicate behind m161.** None in walk 3. m161 is walk 2's page, still
open. `pending_asks` (`rota/roles/principal.py:168-185`) returns every open
message to the principal whose verb is not `converse`, ordered by `seq`,
and it reads no request. The agent principal answers the first ask.

**The predicate behind m186.** `quarantined`
(`rota/core/predicates.py:1465-1536`). s299's ruling on m175 contested the
confirm item. s303 set it `contested`. `contested`
(`predicates.py:236-245`) woke the Vision Keeper three times, s304, s307
and s310, and the key `vision_keeper|tick:contested|confirm_with_default_on_eof`
reached 3 attempts. s313 woke on `tick:quarantined` with the detail `1
abandoned: contested for confirm_with_default_on_eof (vision_keeper), 3
attempts` and refs `["confirm_with_default_on_eof"]`, and sent
`msg.present_principal(refs=['confirm_with_default_on_eof'])`. The send
door, `_bind_send.stage` (`rota/core/sandbox.py:2446-2462`), added
`request_rows(conn, refs)`. `request_rows` (`principal.py:503-542`) reaches
items through `_items_reached` (`principal.py:455-476`), so it returned the
confirm item and its five criteria. `config` `stamped:m186` holds the five
criteria (observed: night 137, 2026-10-10). The walk's own request,
`version_option_show_python`, stood `draft` at version 3 and no ref
reached it. `request_rows` falls back to `open_requests` only when the refs
reach no item.

**What `open_requests` reads** (`principal.py:479-500`). An in-scope item
that cites a ratified statement, is not observed and not a description,
and whose version is above its `delivered:` row. A contested item of an
earlier request matches, for ever. On night 137 the confirm item matches
at version 1 with no `delivered:` row. `version_option_show_python`
matches too. `echo_json` does not, because `delivered:echo_json` is 2 and
its version is 2 (observed: `items` and `config`, night 137, 2026-10-10).

**m192, the sign-off page after m186** (observed: m191 and m192, night
137). s318 woke on `tick:signoff` for the draft `version_option_show_python`.
The Vision Keeper's `submit` m191 named all seven items. The page m192
numbered `version_option_show_python` first, the confirm item second, and
`echo_json` at line 12. The principal asked to remove lines 2 and 12, m193.

### 1.2 Which code carried s299's and s314's words to the confirm item

1. **The page.** m161's refs held the confirm item and its criteria, so
   every numbered line was the confirm request: line 1 the item, lines 2 to
   6 the criteria, lines 7 to 13 the seat notes (observed: s293's prompt,
   `landing.page`, night 137).
2. **The ruling.** s299, in `landing` (`_mode_key`,
   `rota/core/runner.py:258-263`, a principal `converse` whose cause is a
   `present`), sent `rulings.rule` with `contest` on all 13 lines and the
   words "Yes, that's right. Please send the new page for the show_python
   flag on version_option." `rulings_rule` (`rota/roles/api.py:6983-7193`)
   checks that each line is on the page and has a word. It has no notion
   of which request a line belongs to. The ruling r_7d89909888 landed
   (observed: `rulings`, night 137).
3. **The state write.** `land` (`principal.py:1118-1374`) closed the 7
   ledger rows as overruled. It added each row's `about_ref` as `contest`
   when the `about_ref` was not stamped, which put `batch_1_confirm_eof_default`
   into the verdict through two Developer notes. Its item loop
   (`principal.py:1297-1311`) wrote `approval='contested'` on the confirm
   item. `verdict:m176` holds the item, the 5 criteria, the 7 rows and the
   batch (observed: `config`, night 137).
4. **The relay.** s300, `verdict_signoff`, relayed the batch to the
   Architect, the criteria to the Terminologist, and the item to the
   Vision Keeper. s303 set the item `contested` again.
5. **s314 on m186.** The same door and the same `land`: `contest` on lines
   1 to 6. `verdict:m188` holds the item and the 5 criteria. s315 relayed
   the criteria to the Terminologist, m189.
6. **s316.** `_mode_key` keyed the Terminologist's `relay` of criteria to
   `criterion_repair` through `park_criterion_relay`
   (`runner.py:264-275`, `scheduler.py:1714`). The brief respecifies a
   criterion from `principal_said`. s316 called `criteria.respecify` on all
   5 confirm criteria with `show_python` text, 7 calls (observed:
   `tool_calls`, night 137, 2026-10-10).

So no site asks whether a line belongs to the request that the principal
is working on. The page, the ruling door, `land` and the relay each take
the line's row as the target.

### 1.3 How `tick_slicing`, the grouping and the cancel read an item's approval and version

| Site | File and line | What it reads |
|---|---|---|
| `tick_slicing` | `rota/core/scheduler.py:266-341` | `approval = 'approved' AND approval_ver >= version`, not observed, not described, and a version above `delivered:` or above the newest ticket's `item_ver` |
| `tick_criteria` | `scheduler.py:344-358` | tickets with no criteria, not described, not retired. No approval |
| `grouping` | `rota/core/predicates.py:511-545` | criteria whose ticket is in no batch that is not abandoned, not described, not retired. **No approval and no version** |
| `batches.group` | `rota/roles/api.py:4690-4804` | the tickets exist, one item, the wake's tickets, a new id, no live twin. **No approval and no version** |
| `next_batch` | `scheduler.py:1442-1475` | `approval = 'approved' AND approval_ver >= version`, no open predecessor, not parked |
| `cancel` | `predicates.py:1339-1362` | a live batch whose item has `approval != 'approved' OR approval_ver < version`, abandoned by the scheduler |

**Night 137's loop** (observed: `batches`, `sessions`, `tool_calls`,
night 137, 2026-10-10). The confirm item stood `contested`, `approval_ver`
1, version 1, from s303 on. Its ticket `tk_1_confirm_with_default_on_eof`
had criteria and no live batch after `batch_1_confirm_eof_default` was
abandoned. So `grouping` woke the Architect on that ticket. s321 called
`batches.group(id='batch_1_confirm_eof_default', ...)`, was refused for an
old id, and then grouped `batch_1_confirm_eof_default_new`. `cancel`
abandoned it in the next pass. 13 grouping sessions, s321 to s352, opened
13 batches, and each was abandoned at its first wake. 9 of the 13 names
copy the merged `echo_json_group`.

### 1.4 What a park is today

**A park is a batch state** (observed: `scheduler.parked`,
`scheduler.py:1846-1875`, and `park_ask`, `predicates.py:1539-1575`). A
deferred batch whose key was quarantined, or a batch at or past
`loop_cap`, is parked. `next_batch` skips it. `park_ask` owes one ask to
the principal: a page with the item and its criteria when a criterion's
own test is red, and a note otherwise. The park ask's id is `m_park_<...>`.
`close_park_asks` and `close_stale_park_asks` (`scheduler.py:1817-1844`)
close a park ask when its batch leaves the park, and `frontier` calls the
second in every pass (`scheduler.py:1301`).

**The ruling "The park ask is a page with rows"** (`rota/DECISIONS.md`,
2026-10-08) says five things: there is no fix word; the park ask is a
page whose rows are the item's criteria, ruled approve, contest or
revise; the page goes only when a criterion's own test is red, and
otherwise the team writes a note; "Every word of the principal is a ruling
on a row, or it earns one Liaison question that names a row"; and a park
page approved whole is the ceiling.

**An item cannot be parked.** `items.approval` takes `draft`, `pending`,
`approved` or `contested` (`rota/core/schema.sql`, the `items` table). No
column, config row or table says that an item waits. `rulings_rule` takes
`approve`, `contest` and `revise` only (`api.py:7083-7087`). So the system
cannot park an item, the principal cannot park one, and nothing can reopen
one. A put-off request lands as `contest` (frame 185) and wakes the Vision
Keeper to amend it (frame 187).

**The word `reopen` is taken.** The predicate `reopen`
(`predicates.py:855-880`) elects amend or restart for a batch whose item
stopped being approved. This design names the principal's word `resume` in
the code for that reason, and the principal may write "reopen".

### 1.5 Where the Liaison's brief sends the principal's words, and why s293 to s297 asked

A principal `converse` with no cause wakes the Liaison in `converse`
(`rota/roles/prompts/liaison/converse.md`), which holds `brief.intake`
and `brief.segment`. A `converse` whose cause is a `present` or a
`confirm` wakes it in `landing` (`runner.py:258-263`). A `converse` whose
cause is a `clarify` wakes it in `answering` (`runner.py:254-257`).

`landing.md` gives one function, `rulings.rule`, and two uses of `ask`:
"The reply is a question about the page", or "you cannot tell which lines
the reply is about, or whether it agrees". s293's prompt held m161 as the
page, all 13 lines about confirm, and the reply "Line 1 is the wrong
change ... the change I'm working on now is the show_python flag for
version_option". `recent_chat` held the new request and the principal's
"ok" to its confirm (observed: s293's first turn, night 137, 2026-10-10).
No line was about `version_option_show_python`, so the brief's second
case applied, and s293 asked "Could you clarify which lines on the page
relate to this change". s295 and s297 read the same page and the next
reply. Each reply said that no line belongs, and each ask-back asked
again. s299 then read "Yes, that's right. Please send the new page" as a
contest of every line, because the brief says "The reply names the line,
or corrects the thing the line says: `contest`", and a request for a new
page has no other word.

**Night 133's s481** (observed: `tool_calls`, `rulings`, `messages`, night
133, 2026-10-10). s481 woke in `answering` on m350, the reply to the
clarify m347, whose refs are `tk_1_confirm_default_on_eof` and
`tk_1_version_option_show_python`. The reply said "They're independent.
The confirm change is a separate request I'll take up on its own, so leave
it out of this one." s481 ruled `{"tk_1_confirm_default_on_eof":
"contest", "tk_1_version_option_show_python": "approve"}`, r_eb20127f89,
and relayed to the Vision Keeper. s482 set the confirm item `contested`.
`answering.md` offers the same three words.

**Night 137's s159 and s291** (observed: `tool_calls`, night 137,
2026-10-10). s159 sent `rulings.rule(rulings={1: 'approve', 2: 'drop', ...})`
twice, and s291 sent `{..., 8: 'ask'}` twice. The refusal at
`api.py:7084-7086`, `line N: 'drop' is not a ruling. Each line takes
approve, contest or revise`, names no mapping, and the second call was the
first call again.

### 1.6 The four points, by site

| Point | Sites | What the code does today on night 137 |
|---|---|---|
| 1, a request is a boundary | `principal.pending_asks`, `scheduler.frontier`, `principal.request_rows`, `principal.open_requests`, `principal.render_page`, `sandbox._bind_send.stage`, `principal.land`, `api.rulings_rule`, and the predicates `contested`, `quarantined`, `park_ask`, `touch_note`, `signoff`, with `tick_slicing`, `tick_criteria`, `next_batch`, `tick_agenda` | m161 stays open after m_p3 and is answered first. m186 carries the contested confirm item. m192 carries confirm and `echo_json`. s299 and s314 contest the confirm item with words about `version_option_show_python` |
| 2, the grouping | `predicates.grouping`, `api.batches_group` | 13 batches on the contested confirm item, 13 abandoned at their first wake |
| 3, the words | `api.rulings_rule` lines 7083-7087, `landing.md`, `answering.md` | `drop` on m63 and `ask` on m162 drew nothing. Night 133's `separate request` landed as `contest` |
| 4, frame 190's surfaces | `request_block`, `rulings_rule`'s batch-line door, `architect/annotate.md`, `ledger_log` | unchanged by this design |

## 2. The design

Five changes, one per mechanism. Each names its file and function, the new
behaviour, one test on a real turn, and what it does not change. Rota
workflow, except where a line says meta workflow.

The changes rest on these records:

- The shape Roman approved on 2026-10-10 about 03:35, four points, copied
  in the brief of this agent (ruled: Roman, 2026-10-10).
- The composition, Flows: "A question changes nothing. Only a ratified
  amendment to something approved revokes work downstream." And Records:
  "Nothing stops quietly. Every open obligation stays visible and
  countable until something discharges it."
- Law 8: "No batch schedules unless its item's approval postdates the
  item's last amendment."
- Law 9: "A priority change alters no approved content, trips no
  revocation ... and moves batches whole."
- The ruling of 2026-10-08, point 4: "Every word of the principal is a
  ruling on a row, or it earns one Liaison question that names a row."
- The ruling of 2026-09-27 (`scheduler.parked`'s comment): "A given-up
  batch put back in the chair waits for the principal."

**Two words the changes use.**

- A **request** is a principal `converse` to the Liaison with no
  `cause_id`. Its **entry** is the one id in its `body_refs`. A request is
  a **boundary** when its entry is the `span_entry` of a statement, or
  while the request message is still `open`. A request that `converse`
  read as a question or a greeting has no statement and is answered, so it
  is no boundary. The newest boundary is the **current request**.
- An item **belongs to** a request when it cites, through `refs` with kind
  `statement`, a statement whose `span_entry` is that request's entry. An
  **earlier-request item** belongs to a request older than the current
  one, and has no `resume` after the current request (2.5). An observed
  item, a description and `how_it_works` belong to no request.

### 2.1 The request boundary: a page sent before a new request closes

**The mechanism.** When a request lands, every open page to the principal
that was sent before it leaves the principal's view at once, and closes
once the request is read as work.

1. A new helper, `principal.current_request(conn) -> sqlite3.Row | None`,
   returns the newest boundary: its message id, `seq`, entry and the
   entry's `ts_order`. A helper `principal.request_of(conn, item) -> str |
   None` returns the entry of the request an item belongs to.
2. **The read.** `pending_asks` (`principal.py:168-185`) leaves out every
   open ask whose `seq` is below the current request's `seq`. The walk and
   the TUI read `pending_asks`, so the principal never sees m161 after
   m_p3 is inserted. The hide needs no write, so it holds in the step
   before any session runs, which is when the agent principal answered
   m161 on night 137.
3. **The write.** A new function,
   `scheduler.close_pages_before_request(conn) -> int`, runs in `frontier`
   (`scheduler.py:1269-1310`) beside `close_stale_park_asks`. When the
   current request has a statement, it sets each open message to the
   principal with a lower `seq` to `answered`, and writes the config row
   `closed:<message id>` with the request's message id. A ruling that the
   Liaison staged on a closed page lands nothing: `land` already returns
   None for a page that is not open, and `apply_rulings` marks the row
   `stale` (`principal.py:1147-1150`, `1377-1409`).
4. A request that `converse` reads as a question has no statement. Its
   message is answered by the session's commit, so it is no boundary, and
   the hidden pages come back in the next read.
5. The ledger rows of a closed page stay `open` and countable. They reach
   the principal again on a later page, under the order of 2.2's point 5.
6. `render_state` (`principal.py:201`) gains one line per closed page:
   "Set aside when you asked for <the request's first statement>: <n>
   lines." The record stays visible, as the composition's Records ask.

**What it does not change.** A page sent after the request stays, whatever
it is about. A request that arrives while no page is open closes nothing.
The park ask and the touch note close as any page does.

**The test.** Night 137, s293's turn. Rebuild inline m161 at seq 163 with
its 13 refs and `stamped:m161`, m162 answered, m_p3 at seq 165 open with
`["e_p3"]`, the entries `e_p1` to `e_p3`, the statements s1 and s2
ratified, and no s3. `pending_asks` returns nothing. Add s3 `proposed`
from `e_p3`, and set m_p3 `answered`. `frontier` runs, m161 is `answered`,
and `closed:m161` holds `m_p3`. A ruling row staged on m161, s299's map
with m175's words, goes `stale` through `apply_rulings`, and the confirm
item stays `approved` at version 1. A second case: m_p3 answered with no
statement, as a question, and `pending_asks` returns m161 again.

### 2.2 The park: an earlier request's contested or draft item parks, and every reader skips it

**The mechanism.** When a request becomes the current request, each
earlier-request item that is `contested` or `draft` at that moment parks.
A parked item wakes no seat and opens no batch until the principal resumes
it. An approved item of an earlier request is not parked, and its batch
keeps its place, because only a ratified amendment revokes approved work
(the composition, Flows). A merged item is not parked, because it is
delivered.

1. **The record.** A new table `item_parks` in `rota/core/schema.sql`:
   `id` (a hash of the item and the cause, law 14), `item_id`, `kind`
   (`park` or `resume`), `by` (`request` or `principal`), `cause_id` (the
   request message or the principal's verdict message), and `seq` (the
   cause's `seq`). Each row has one writer: `close_pages_before_request`
   writes the `request` rows, and `land` writes the `principal` rows
   (2.5). An item is parked when its newest row is `park`. `CREATE TABLE IF
   NOT EXISTS` adds the table to an old database, and a reader of a
   database with no table reads no park.
2. **The write.** `close_pages_before_request` (2.1), in the same pass,
   writes one `request` row for each earlier-request item that is
   `contested` or `draft` and has no row for this request. The state is
   read at the boundary and written once, so a later contest of an
   approved item on its own page does not park it.
3. **The helper.** `scheduler.not_parked(conn, col, of="item")`, the shape
   of `not_described` and `not_retired` (`scheduler.py:228-264`): an SQL
   condition that drops a parked item, or the ticket or batch of one. It
   is empty when the table is missing.
4. **The readers.** Each of these adds `not_parked`:
   - `contested` (`predicates.py:236-245`). A parked contested item wakes
     no Vision Keeper. Night 137's s304, s307 and s310 had this shape
     after the item went contested.
   - `signoff`, through `tick_signoff` (`scheduler.py:440-462`). A parked
     draft is not submitted.
   - `tick_slicing` (`scheduler.py:266-341`) and `tick_criteria`
     (`scheduler.py:344-358`).
   - `grouping` (`predicates.py:511-545`), beside 2.4's guard.
   - `next_batch` (`scheduler.py:1442-1475`). A batch of a parked item
     does not start. `preempt` (`predicates.py:1365`) also defers a
     running batch whose item is parked, through the existing
     `do:preempt`, so its worktree and commits persist as deferred work
     (law 9's preemption).
   - `park_ask` (`predicates.py:1539-1575`) and `touch_note`
     (`predicates.py:776-806`). A parked item's batch owes no page while it
     waits.
   - `quarantined` (`predicates.py:1465-1536`). A key whose refs reach only
     parked items is skipped, as a key that a park owns is skipped today.
     Night 137's m186 had this shape.
5. **The agenda's order.** `tick_agenda` (`scheduler.py:967-1034`) skips an
   open ledger row whose `about_ref` reaches only parked items, through
   `_items_reached`. It orders the rest as the current request's rows
   first, then rows that reach no request, then rows of an approved
   earlier request. No row is dropped: an approved request's assumptions
   still reach a page before its merge, by law 8.
6. **What the cancel does.** `cancel` (`predicates.py:1339-1362`) is
   unchanged. A contested parked item's live batch is abandoned as today,
   and the item's ticket waits in no batch. On a `resume` the grouping
   offers it again.

**What it does not change.** The approval of a parked item. A park writes
no `items` row, so a `resume` returns the item to the state it held:
`contested` wakes the Vision Keeper with the newest verdict's words,
`draft` goes to the sign-off. An approved earlier request builds under law
9's priority, and its own owed pages still reach the principal: the park
page by the ruling of 2026-09-27, and its touch note. Those pages carry
that request's lines alone, by 2.3.

**The test.** Night 137, s313's dispatch. Rebuild inline the confirm item
`contested` at version 1 with its ticket and 5 criteria,
`version_option_show_python` `draft` at version 3 with s3 `ratified`,
`echo_json` with `delivered:echo_json` at 2, m_p3, and the quarantined key
`vision_keeper|tick:contested|confirm_with_default_on_eof` at 3 attempts
with `reported` 0. Before the pass, `contested` and `quarantined` each
return one wake on the confirm item, as on the night. After
`close_pages_before_request`, `item_parks` holds one `request` row for
the confirm item and none for `echo_json` or `version_option_show_python`.
Then `contested`, `quarantined` and `grouping` return no wake on it, and
`signoff` returns `version_option_show_python` alone. On night 137 the
confirm item went contested after m_p3, so this test holds the item
contested at the boundary on purpose. The rows are the night's, and the
order is the case 2.2 exists for (reasoned: the design's own case).

### 2.3 One request per page: a page carries its request's lines, and words on it never change another request's item

**The mechanism.** A page is about one request. Its numbered request lines
are that request's items and criteria, and each parked item gets one
waiting line. A ruling on that page writes nothing on an item of another
request.

1. **The page's request.** A new helper, `principal.page_request(conn,
   refs) -> str | None`, returns the newest request that the page's refs
   reach. A page sent after the current request whose refs reach the
   current request, or reach no request, is the current request's page.
   An approved earlier request's own owed page, a park page or a touch
   note whose refs reach only that request, is that request's page.
2. **`request_rows`** (`principal.py:503-542`) returns the items of the
   page's request and their criteria, then one row per parked item, then
   nothing else. The fallback through `open_requests` returns the current
   request's open items only, plus a resumed item. The send door stamps
   these rows as today (`sandbox.py:2446-2462`).
3. **`render_page`** (`principal.py:733-950`) drops from every group a row
   whose items, by `_items_reached`, are all items of another request, or
   all delivered items of an earlier request. A row that reaches no item
   stays. On night 137's m192 this drops the confirm item, its five
   criteria and `echo_json`, which are lines 2 to 7 and 12 on the night.
4. **The waiting line.** `request_block` (`principal.py:576-655`) numbers
   each parked item after the request's own lines under one heading,
   "Waiting:", with one line: "<item text>. You put this aside when you
   asked for the change above. To take it up again, say reopen line <n>."
   The item's criteria and notes are not numbered. The line counts the
   open ledger rows that reach the item: "<k> notes wait with it."
5. **The door.** `rulings_rule` (`api.py:6983-7193`), after each key maps
   to a row:
   - A `contest` or a `revise` of a row whose items all belong to another
     request than the page's is refused: "line <n> is your earlier
     request, <item>, which waits. Words on this page do not change it.
     To take it up again, rule line <n> resume. To leave it waiting,
     approve the line."
   - On a clarify, whose keys are row ids, the same refusal names the row
     and adds "To put it aside, rule it later." s481's ticket of the
     earlier request reads this refusal.
6. **The guard in `land`.** `land` (`principal.py:1218-1311`) writes no
   approval on a parked item and no approval on an item of another request
   than the page's, whatever the ruling. Only `resume` and `park` (2.5)
   write, and they write `item_parks` rows. The sign-off page needs this
   guard: the Vision Keeper's `submit` names every item, so the confirm
   item is a wake row on m192 and not a stamped row, and frame 190's
   stamped filter at line 1219 would let an "ok" approve it.

**What it does not change.** The request block, its "You asked:" and "It
must:" headings, the team's notes heading, the batch-line door and the
quarantined branch of frame 190's design stay as built (Roman's point 4).
A page with no request item, the onboarding account page, renders as
today.

**The test.** Night 137, s299's turn and m192's render. First case: rebuild
inline the rows of m192 with walk 3's request current, the confirm item
parked by a `request` row, and `echo_json` delivered. `render_page`
numbers `version_option_show_python` as line 1, then the account lines,
then one waiting line for the confirm item, and no line for `echo_json` or
the five confirm criteria. `order` holds no confirm criterion. The call
`rulings.rule(rulings={<every line>: "approve"}, words="ok")` lands, and
the confirm item is still `contested` with its `request` park row the
newest. Second case: a page of the current request that still numbers the
confirm item, built by giving the present the confirm item as a ref. s299's
map, `contest` on every line with m175's words, is refused with the line
of the confirm item named.

### 2.4 The grouping opens no batch on an item whose approval does not cover its version

**The mechanism.** The grouping reads the item's approval as `next_batch`
does.

1. `grouping` (`predicates.py:511-545`) adds one condition: the ticket's
   item is `approved` with `approval_ver >= version`, and not parked
   (2.2). The `WHERE` joins `tickets` to `items` on `item_id`, the same
   test as `next_batch` (`scheduler.py:1454-1456`) and the complement of
   `cancel`'s.
2. `batches_group` (`api.py:4690-4804`) refuses an item that is not
   approved at its version, after `_must_exist(ctx, "items", item_id)`:
   "<item> is <approval> at version <v>, so no batch can run it: the cancel
   would abandon it at once. A batch waits for the principal's approval of
   the item's current version. Group nothing for it, and stop." The door
   is the belt for a wake that predates the state, and for a seat that
   names an item the wake did not carry.

**What it does not change.** `cancel`, `next_batch` and `tick_slicing`. A
contested item's ticket still has no live batch, and the grouping offers
it again once the item is approved at its version. The `grouping.md`
brief does not change, because the wake no longer fires.

**The test.** Night 137, s321's dispatch. Rebuild inline the confirm item
`contested`, `approval_ver` 1, version 1, its ticket
`tk_1_confirm_with_default_on_eof` with `item_ver` 1, its 5 criteria,
`batch_1_confirm_eof_default` `abandoned` with head commit 34a5e21, and
`echo_json_group` merged. `grouping` returns no wake. Set the item
`approved` at version 1, and `grouping` returns one wake on the ticket. A
second case: the call `batches.group(id='batch_1_confirm_eof_default_new',
item_id='confirm_with_default_on_eof',
ticket_ids=['tk_1_confirm_with_default_on_eof'])` in a session with the
contested item is refused with the sentence of point 2. Night 133's s564
and s565 are the same shape and are not rebuilt.

### 2.5 The words door: a principal word that the three ruling words do not hold lands by one named mapping

**The mechanism.** `rulings_rule` maps a known word to its effect, lands
it, and names the mapping in the refusal of an unknown word.

1. **The map**, a constant `RULING_WORDS` in `rota/roles/api.py`, beside
   `rulings_rule`:

   | Words | Effect | Stored as |
   |---|---|---|
   | approve, contest, revise | as today | the word |
   | drop, remove, strike | a contest of the line | `contest` |
   | later, separate, park, defer | a park of the item the line reaches (frame 185's deferral) | `park` |
   | resume, reopen | a resume of a parked item | `resume` |
   | ask, unclear, question | a question back | refused, with the call named |

   A word is read lower-case and stripped. A phrase such as "separate
   request" maps by its first word when that word is in the map.
2. **`ask` is refused with the call that lands it.** "line <n>: 'ask' is a
   question back, and a question is its own call:
   rulings.rule(ask=\"<one sentence about line <n>>\") with no rulings."
   The door cannot write the sentence, because the Liaison originates the
   question and the question names the row (the composition, the
   Liaison). s291's second call then differs from its first (reasoned:
   the refusal names a call that the first call was not).
3. **An unknown word** is refused with the whole map: "line <n>: '<word>'
   is not a ruling. Each line takes approve, contest or revise. drop,
   remove and strike are contest. later and separate put the item aside:
   park. reopen and resume take a waiting item up again: resume. ask,
   unclear and question are a question: rulings.rule(ask=...) with no
   rulings."
4. **`park`.** The door maps the line to its request item through
   `_items_reached`. A line that reaches no request item is refused: "line
   <n> reaches no request. later puts a request aside, so rule the line of
   the request." The ruling keeps `{<item>: "park"}`, and a criterion or
   ledger line of that item leaves the map, so no relay carries it. `land`
   writes one `principal` row `park` in `item_parks` with the verdict's id
   and `seq`, writes no `items` row, and leaves the item out of the
   verdict's refs. A page whose every line is the parked item or approve
   closes and wakes nobody, as an all-approve page does today.
5. **`resume`.** Admitted only on a waiting line (2.3) or a parked item's
   row. `land` writes one `principal` row `resume`. On any other line the
   door refuses: "line <n> is not waiting. resume takes up a request you
   put aside."
6. **The briefs.** `landing.md` and `answering.md` each gain one bullet
   after the `revise` bullet:

   ```
   - The reply puts the line off to a separate or later request: `later`.
     The item waits, and nothing about it is changed.
   - The reply takes a waiting line up again: `resume`.
   ```

   `landing.md` keeps "Each line takes approve, contest or revise" as its
   main sentence, because the door maps the other words.

**What it does not change.** The three ruling words, their meaning, and the
rule that every line takes one. The refusal of a call with an unclosed
quote, s320 on m193, frame 137's family.

**The test.** Three real turns. Night 133, s481's turn on m350: rebuild
inline the clarify m347 with its two tickets, the confirm item and the
version item with their statements s2 and s3, and m_p3 at seq 258. The
call `rulings.rule(rulings={"tk_1_confirm_default_on_eof": "later",
"tk_1_version_option_show_python": "approve"}, words=<m350's words>)` is
admitted. After `apply_rulings`, `item_parks` holds one `principal` row
`park` for `confirm_default_on_eof`, the item's approval is unchanged, and
no relay to the Vision Keeper names it. Night 137, s159's turn on m63, the
answer to m62: the call with `drop` on lines 2 to 8 is admitted, and the ruling holds
`contest` on those lines. Night 137, s291's turn on m162, the answer to m161: the
call with `ask` on line 8 is refused with the sentence of point 2, and the same
call with `ask="<a sentence about line 8>"` and no rulings is admitted.

### 2.6 What stays as frame 190 built it

The request-first page (`request_rows`, `request_block`, the team's notes
heading), the correction of a predicted file (the batch-line door before
the head commit, the Architect's `annotate` relay), and the Architect's
reply doors (`ledger.log`'s ruled-row door, the four-word floor, the
message door) keep their behaviour (ruled: Roman, 2026-10-10, point 4).
2.3 adds a filter before `request_rows` returns and a heading after
`request_block`'s lines. It changes neither function's rows for a page of
one request.

### 2.7 The frames, in one table

| Frame | Change | Covered | Left open |
|---|---|---|---|
| 190's narrowed wall, a second request's words on the first request's page and item | 2.1, 2.3 | whole: the page closes before the principal reads it, and a ruling on another request's line is refused | none in the mechanism. The ratio is the night's |
| 185, `a separate request, for later` | 2.5 point 4, 2.2 | whole for the mechanism: `later` parks the item, and the parked item leaves every page but its waiting line | the ratio, read on the night |
| 186, the grouping on a contested item | 2.4 | whole | none |
| 192, `drop` | 2.5 points 1 to 3 | `drop` whole. `ask` in part: the refusal names the call, so the answer lands on the second call | the unclosed quote of s320, frame 137's family |
| 187, the contested tick re-wakes the Vision Keeper | 2.2 point 4 | in part: a parked contested item wakes no Vision Keeper | the re-wake on a current request's contested item |
| 41's wall, a page open at a walk's end | 2.1 | in part: when the next walk carries a new request | a walk that continues the same request. Open question 5.1 on onboarding pages |
| 184, the ask-back copy | none | none | all |

### 2.F Amendments from Roman's ruling and the design review of 2026-10-10

Roman ruled on 2026-10-10 at 04:33 that a request boundary is a question to
the principal, not a silent park (ruled: Roman, "Why not ask you blocking
questions if you're there? There's enough context to explain the shift in
focus", copied from `plans/stack.md`, frame 193, the status line of 04:33).
This section replaces change 2.2 whole, the close of change 2.1, the
waiting line of change 2.3, the words `later` and `reopen` of change 2.5,
and section 6.
Where this section and sections 2.1 to 2.5 differ, this section wins. The
design review on Opus, 2026-10-10 04:24, found 6 high and 6 low. Each
finding is answered in 2.F.9 (copied: the stack's status line of 04:24, and
the probes `p0_schema.py` to `p20_reach.py` in the scratchpad folder `r193`
of session 45fc3fe2, read-only). Rota workflow, except 2.F.10 and 2.F.11,
which are meta workflow.

#### 2.F.1 The shift question: its wake

**When it fires.** A new predicate `request_shift` in
`rota/core/predicates.py`, band `traffic`, wakes the Liaison. It fires when
the current request (2.1, as amended by 2.F.6) has a statement, and an
**open earlier request** exists: an item that belongs to an earlier request,
is not delivered, holds no shift ruling for this current request, and is
`approved`, `contested` or `draft`. Roman's words name approved and
building, and contested. A draft is included, because a draft earlier item
is submitted again by `signoff` and reaches the principal in the same way
(reasoned: `tick_signoff`, `scheduler.py:440-462`, submits every draft).
One wake per open earlier item, the oldest request first, refs
`(<A item>, <B statement>)`. The detail carries the facts the page needs, so
the brief has no lookup to do (2.F.2).

**What it holds while it is open.** A question changes nothing (the
composition, Flows), so no state moves while the question is open. A's
approved batch keeps building. The question blocks the principal's view
only:

1. `pending_asks` (`principal.py:168-185`) returns the open shift question
   alone while one is open. Every other open ask waits, unchanged and open.
2. `tick_agenda` (`scheduler.py:967-1034`) and `tick_signoff`
   (`scheduler.py:440-462`) count an open shift question as an open ask, as
   today, so neither sends a page beside it.
3. A's pages sent before B stay `open`. Nothing closes them while the
   question is open. This replaces 2.1's point 3, the close by `seq`.

2.1's read-time hide by `seq` stays for the step between B's insert and
B's statement, so the agent principal does not answer m161 first, as on
night 137 at seq 166 (observed: section 1.1).

#### 2.F.2 The shift question: its page

The page is a present built by the door, as the park page is
(`_park_page`, `principal.py:695-731`). The Liaison wakes in a new mode,
`request_shift`, whose `.tools` hold `msg.present_principal` alone. Its
brief is three sentences: "The principal asked for something new while an
earlier request is still open. Send one `msg.present_principal` with the
refs of your wake. The page says the rest." The id is
`m_shift_<A item>_<B message>`, so the door refuses a second shift page for
the same pair, as `park_ask_id` does for a park.

`render_page` gains a branch, `_shift_page`, before the touch-note branch.
For night 137's A, it reads (reasoned: the rows of night 137 at s292's
commit, section 1.1):

```
You asked for something new: Give version_option a show_python flag that appends the running Python version to the message.
Before that you asked for this, and it is not finished:
  1. Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting.
     Where it stands: approved. The change batch_1_confirm_eof_default is built, and 3 of its 6 tests fail.
     What it waits on: one page to you with 13 lines, and 19 notes.
Choose one for line 1:
  - later: put it aside until the new request is merged. Nothing more about it reaches you until then.
  - now: answer its open page first, then the new request.
  - drop: stop it. Its change is abandoned.
```

"Where it stands" reads the item's approval, its live batch, the batch's
head commit, and the newest test run (`_resume_detail`,
`scheduler.py:420-437`). "What it waits on" counts A's open asks, read
with the hold of 2.F.1, and A's open ledger rows, through `_items_reached`
with the prefix fix of 2.F.9, finding 7.

#### 2.F.3 The three answers, as rulings, and what each writes

The shift page has one numbered line, the A item. It takes one of three
words. The words door of 2.5 maps them on this page alone:

| The principal's word | Stored as | What `land` writes |
|---|---|---|
| later, separate, park, aside, behind | `park` | one `item_parks` row `park`, by `principal`, cause the verdict. A's held asks stay open and held (2.F.4) |
| now, answer, first | `now` | one `item_parks` row `now`. The hold of A's open asks ends, and `pending_asks` shows them before B's asks, by `seq` |
| drop, remove, stop | `drop` | one `item_parks` row `drop`. Every open ask of A closes, each with the config row `closed:<message>` = the verdict id. A's open ledger rows close as overruled, with the principal's words, by the existing ledger branch of `land` (`principal.py:1247-1284`) |

- `approve`, `contest` and `revise` on the shift line are refused: "line 1
  takes later, now or drop: the question is which request goes first, and
  nothing about the request itself changes here."
- None of the three writes `items`. A `drop` makes the item unschedulable
  through the readers of 2.F.4, so `cancel` abandons A's live batch: `cancel`
  (`predicates.py:1339-1362`) adds `OR` the item's newest `item_parks` row is
  `drop`. Law 9's cascade then runs as for any revocation.
- The verdict carries no ref of the shift line, so no relay wakes a seat.
  A shift page ruled whole closes and wakes nobody, as an all-approve page
  does today.
- 2.2's park by state is gone. No row `by = 'request'` is written at a
  boundary. A is never parked without the principal's word (ruled: Roman,
  2026-10-10 04:33).

#### 2.F.4 The park, and its way back

**While A is parked.** `item_parks` (2.2 point 1) stays as the record, with
kinds `park`, `now`, `drop` and `resume`. The readers of 2.2 point 4 read
the newest row, and skip an item whose newest row is `park` or `drop`:
`contested`, `tick_signoff`, `tick_slicing`, `tick_criteria`, `grouping`,
`next_batch`, `park_ask`, `touch_note` and `quarantined`. `preempt` defers a
running batch whose item is parked, through `do:preempt`. A's open asks stay
`open` and `pending_asks` holds them: an open ask whose refs reach only a
parked item is not returned, and `tick_agenda` and `tick_signoff` do not
count it as open (2.F.9, finding 5 and finding 8).

**The way back, by itself.** "Later" means behind the current request. A
new function, `scheduler.resume_behind(conn)`, runs in `frontier` beside
`close_stale_park_asks`. When the request that the park named as current
is delivered, its items at their `delivered:` version, or dropped, it
writes one `item_parks` row `resume`, `by = 'request'`, cause that
request's message. The parked item then reads as it did before the park:
its held asks return to `pending_asks`, and its work wakes again. Its rows
are written by `resume_behind` alone, and `land` writes the principal's
rows, so each row has one writer.

**The way back, by the principal.** The word `resume` on a line of a parked
item, through 2.F.5's list, or a later shift page. `reopen` is not a stored
value and not a mapped word (2.F.9, finding 10).

**`render_state`** (`principal.py:201`) gains one block, "Waiting behind
<B's statement>:", one line per parked item: its text, its open asks, its
open notes, and "It comes back when that request is merged, or say resume."
A dropped item has one line under "Dropped:".

**The walk's quiet end.** A walk that goes quiet while an item is parked and
its current request is neither delivered nor dropped prints one line, for
the read, from `probes/walk.py`'s quiet branch: "QUIET with waiting: <item>,
behind <B>". Meta workflow. On a quiet with B delivered, `resume_behind` has
already resumed A, so the loop is not quiet.

#### 2.F.5 The words door, amended

The map of 2.5 point 1 becomes two maps, and pass 1 ships the first alone:

| Page | Words | Stored as |
|---|---|---|
| any page but the shift page | approve, contest, revise | the word |
| any page but the shift page | drop, remove, strike | `contest` |
| any page but the shift page | ask, unclear, question | refused, with `rulings.rule(ask=...)` named |
| any page but the shift page | resume | `resume`, on a parked item's line only (pass 2) |
| the shift page | later, separate, park, aside, behind / now, answer, first / drop, remove, stop | `park` / `now` / `drop` (pass 2) |

- `later` and `separate` leave the general map. A put-off request is now
  the shift question's, which names the item and the request it waits
  behind. On a page of the current request, a line about an earlier
  request does not exist after 2.3, so the word has no line to land on.
- On an earlier request's own page after the shift question, which the
  principal sees only after `now` or a `resume`, `drop` and `remove` on a
  line contest that line, because the principal chose to work on that
  request. Night 133's eight answers that hold "separate request" and
  "drop" in one sentence all fall on pages of a request the principal had
  moved past (copied: the review's `p10_words.out` and `p11_words2.out`).
  After 2.F.1, those pages are held behind the shift question, so the
  sentence reaches the shift page, where `drop` means drop the request and
  `separate` means later. The Liaison's `landing.md` gains one bullet for
  the shift page: "The page asks which request goes first. A reply that
  says the earlier one is separate or for later is `later`, even when it
  also says drop it from this change."
- The unknown-word refusal names the map of the page it is on.

#### 2.F.6 The follow-up on the same request is no boundary

A principal `converse` with no cause and a statement is a boundary only
when one of its statements is a new request. A statement that supersedes a
statement of the current request, or clarifies one, is a follow-up.

1. `brief.segment` (`api.py`, the `brief_segment` op) gains an optional
   argument, `supersedes`, a statement id. The door admits only a ratified
   statement of the current request, and writes the column
   `statements.supersedes`, which exists and has no writer today (observed:
   `grep supersedes rota`, 2026-10-10). The ratification sets the older
   statement `clarified`, a status the schema already holds.
2. `current_request` (2.1) skips a request whose every statement has
   `supersedes`. So a follow-up keeps the current request, and its pages
   stay.
3. `converse.md` gains one paragraph after "Work only when obvious": "When
   the words change or add to the request on the principal's current page,
   segment them with `supersedes` set to that request's statement. That is
   the same request, said again." The working set of a `converse` wake
   gains `current_request`, the statement id and text, so the seat has the
   id to copy.

The review read this as a risk on any night with a follow-up (reasoned:
the review's finding 6). Neither night 133 nor night 137 sent an uncaused
follow-up, so no real turn tests it, and the test is the inline case of
2.F.10.

**Amended at pass 2c, 2026-10-10** (observed: the diff review of 61a0f41d, probe `p7_segment.py`): the ratification writes no `clarified` row. With the older statement `clarified`, `open_requests` lost the current item and the new statement read as uncovered. The older statement stays `ratified`, and `uncovered_statements` follows `supersedes` to the root, so an item that cites either statement covers both. No writer of `clarified` is left. Meta workflow.

#### 2.F.7 Change 2.3, amended

- `request_rows` and `render_page` keep 2.3's rule, one request per page,
  with two changes. A parked or dropped item has no line on any page but
  its own shift page. The waiting line of 2.3 point 4 goes, because
  `render_state` carries the way back (2.F.4) and the shift page carries the
  choice.
- **No ref rides a page unnumbered.** The send door `_bind_send.stage`
  (`sandbox.py:2436-2462`) removes from a present's refs every row that
  `render_page` would drop, before it writes the message. So the message's
  refs and the page's numbered rows are the same set, and a ruling of the
  page closes each row it holds. A row that is dropped stays `open` and
  countable on `render_state`.
- **A delivered earlier item's notes.** 2.3 point 3 dropped a row that
  reaches a delivered item of an earlier request. That rule goes. Such a
  row, night 137's six `echo_json` rows, renders under the team's notes as
  any note does, and a ruling closes it (2.F.9, finding 4). The delivered
  item's own line still does not render on another request's page.

#### 2.F.8 Change 2.4, amended

`batches_group` refuses only the item that is not approved at its version,
and names the tickets of the wake that it would admit: "<item> is
<approval> at version <v>, so no batch can run it. Group the other tickets
of your wake, <tickets>, and leave <item>'s." With no other ticket, the
sentence ends "Group nothing, and stop." The predicate of 2.4 point 1
already leaves an unapproved item's tickets out of the wake, so the refusal
fires only for a stale wake or a named item outside it.

#### 2.F.9 The review's twelve findings, and the answers

| # | Finding | Rating | The answer |
|---|---|---|---|
| 1 | The boundary park reads contested or draft alone. On both nights the earlier item was `approved` when the new request landed, s224 on night 137 and s365 on night 133, so 2.2 parks nothing and the confirm pages still reach the principal | high | Dissolved by the ruling. The shift question fires for an approved, contested or draft earlier item (2.F.1), and A's pages are held until the principal answers |
| 2 | After m161 closes, 19 open ledger rows reach the confirm item, and the agenda makes up to 3 confirm pages whose contest lands on the confirm item again | high | No close by `seq` (2.F.1). While the question is open and after `later`, `tick_agenda` skips a row that reaches only a held or parked item (2.F.4). After `drop`, `land` closes the 19 rows as overruled (2.F.3). After `now`, the rows are A's own and land on A's page |
| 3 | Night 133 has 8 answers with "separate request" and "drop" in one sentence, so `drop` to contest on a moved-past request's line lands frame 185's contest with no refusal | high | Those pages are held behind the shift question, and on the shift page `drop` drops the request and `separate` is `later`, with one `landing.md` bullet that ranks `later` first (2.F.5) |
| 4 | Six `echo_json` rows reach a delivered item. 2.3 drops them from the render, no ruling closes them, and they ride every agenda page | high | 2.3's drop of a delivered item's rows goes, and the door keeps a page's refs equal to its numbered rows (2.F.7, `_bind_send.stage`) |
| 5 | A closed park note reads as rested, so the park ask never asks again | high | Nothing closes A's park ask on `later`: it stays open and held, `park_message_rests` (`scheduler.py:1603-1624`) reads it as open, and it shows again on `resume`. On `drop`, `cancel` abandons the batch and `close_stale_park_asks` closes the ask, as for any abandoned batch (2.F.4) |
| 6 | Any uncaused converse with a statement is a boundary, so a follow-up on the same request closes its own pages | high | A statement with `supersedes` is a follow-up, and `current_request` skips it (2.F.6, `brief_segment`, `converse.md`) |
| 7 | `_items_reached` misses an `items:` prefix | low | `_items_reached` (`principal.py:455-476`) strips a leading `<table>:` before its lookups. On night 137, `challenge_items_confirm_with_default_on_eof` has `about_ref` `items:confirm_with_default_on_eof` and reaches nothing today (observed: the review's `p20_reach.py`, 2026-10-10) |
| 8 | The close status `answered` trips invariant I9 | low | Only `drop` closes asks now, and it writes `closed:<message>` with the verdict id. `i9` (`rota/tools/invariants.py:221-248`) skips a message with a `closed:` row, beside its three kinds answered by design. A held ask stays open, so I9 does not read it |
| 9 | No page lists a parked item after the current request merges | low | `resume_behind` resumes it when the current request is delivered, and `render_state` lists it while it waits (2.F.4) |
| 10 | `reopen` on night 136 means the opposite three times | low | `reopen` is neither a stored value nor a mapped word. The way back is `resume`, or the automatic resume (2.F.4, 2.F.5) |
| 11 | The grouping refusal can end a session that holds a legitimate ticket | low | The refusal names the admissible tickets of the wake and asks the seat to group them (2.F.8) |
| 12 | The price is about 2.5M and not 1.5M | low | Taken (2.F.11) |

Point 6 of the review held both recommended answers of section 5 against
Roman's transcripts (copied: the stack's status line of 04:24). Open
question 1 stands as written, with one change: under 2.F.1 an onboarding
page is held only when it reaches an open earlier request, so the question
is about the onboarding page alone. Open question 2 is answered by 2.F.4.
Open question 3 is gone, because the waiting line is gone.

#### 2.F.10 The passes, and the tests on real turns

**Pass 1, small: change 2.4 with 2.F.8, and the words door of 2.F.5 for
pages other than the shift page, without `park`, `now`, `drop` or `resume`
as stored values.** Files: `rota/core/predicates.py` (`grouping`),
`rota/roles/api.py` (`RULING_WORDS`, `rulings_rule`, `batches_group`), the
two briefs `liaison/landing.md` and `liaison/answering.md` with the `drop`
and `ask` lines only, and the tests. Tests on real turns:

- night 137, s321's dispatch and call: `grouping` returns no wake on the
  contested confirm ticket, and the call is refused with the sentence of
  2.F.8 (2.4's test);
- night 137, s159 on m63: `drop` on lines 2 to 8 lands as `contest`;
- night 137, s291 on m162: `ask` on line 8 is refused with the call named,
  and the named call is admitted.

Re-records: the 7 `l1_landing.yaml` cases and
`L1-LI-a-reply-reaches-the-desk-that-asked`, because the briefs change. One
new case, `L1-LI-a-dropped-line-is-a-contest`, at 5 runs. The gate's stale
line decides the rest.

**Pass 2: the shift question and its three answers, with 2.1's hide, 2.3
as amended by 2.F.7, 2.F.4, 2.F.6 and the findings 7 and 8.** Files:
`rota/core/predicates.py` (`request_shift`, `contested`, `park_ask`,
`touch_note`, `quarantined`, `preempt`, `cancel`), `rota/core/scheduler.py`
(`not_parked`, `resume_behind`, `frontier`, `tick_signoff`, `tick_slicing`,
`tick_criteria`, `next_batch`, `tick_agenda`), `rota/roles/principal.py`
(`current_request`, `page_request`, `pending_asks`, `request_rows`,
`render_page` with `_shift_page`, `render_state`, `_items_reached`,
`land`), `rota/core/sandbox.py` (`_bind_send.stage`, the shift page's id),
`rota/roles/api.py` (`brief_segment`, the shift map in `rulings_rule`),
`rota/core/runner.py` (`_mode_key` for `request_shift`, the `converse`
working set), `rota/core/schema.sql` (`item_parks`),
`rota/tools/invariants.py` (`i9`), the briefs
`liaison/request_shift.md` and `.tools`, `liaison/converse.md` and
`liaison/landing.md`, and `probes/walk.py`'s quiet line. Tests on real
turns:

- night 137, s292 to s299: rebuild inline the rows at s292's commit, m161
  open at seq 163, m_p3 answered with s3 `proposed`, the confirm item
  `approved` at version 1 with `batch_1_confirm_eof_default` built to
  34a5e21, and the 7 rows of m161. `request_shift` returns one wake on the
  confirm item. The door's page reads as 2.F.2. `pending_asks` returns the
  shift page alone. The ruling `{"1": "later"}` with m163's words writes
  one `item_parks` row `park`, and the confirm item stays `approved`.
  `pending_asks` then returns m164 and not m161, `tick_agenda` picks none
  of m161's rows, and s299's map of 13 contests on m161 is never asked
  for. A second case rules `drop`: m161 closes with `closed:m161`, the 7
  rows close as overruled, `cancel` abandons the batch, and `i9` reads no
  finding on m161. A third case rules `now`: m161 returns before m164;
- night 137, after the park of the first case: `version_option_show_python`
  delivered, and `resume_behind` writes `resume`, and m161 returns;
- night 133, s383's commit: rebuild inline m_p3 at seq 258, s3, the confirm
  item `approved` as s365 left it, its ticket, and the version item.
  `request_shift` returns one wake on `confirm_default_on_eof`. After the
  ruling `later`, `grouping` offers `tk_1_version_option_show_python` alone,
  which is s477's shape without the confirm ticket;
- night 137, m192's refs with the confirm item parked: no confirm line,
  `echo_json` not numbered as a request line, and the door's refs equal
  the numbered rows (2.F.7);
- night 137, `challenge_items_confirm_with_default_on_eof`:
  `_items_reached` returns the confirm item;
- an inline follow-up, not a night turn: a second uncaused converse whose
  statement supersedes s3 is no boundary, and `request_shift` does not
  fire.

Re-records: every case whose prompt is `converse.md`, in
`g1_segments.yaml`, `l1_liaison.yaml` and `l3_handoffs.yaml`, because
`converse.md` changes and its working set gains `current_request`; the 7
landing cases again, for the shift bullet. Two new cases at 5 runs:
`L1-LI-ask-which-request-goes-first`, the `request_shift` wake of night
137's s292 commit, expecting one present to the principal; and
`L1-LI-a-separate-request-is-later`, night 133's m350 words on a shift page,
expecting `{"1": "later"}`. The scenes `two_batches` and `merged_then_next`
say a second item. `two_batches` says it while item 1 is approved and
deferred, so the shift question fires there and the scene must answer it:
the scene's walk answers `now`, which keeps its park page and its order.
The scene tests decide `merged_then_next`, where item 1 is delivered and no
question fires (reasoned: 2.F.1's rule).

#### 2.F.11 The price

On frame 190's actuals: a designed pass of 291.1k to 307.3k, a small pass
of 93.7k, a review of 132.7k to 213.8k, fix passes and delta reviews of
about 230k each in all, and a night read of 353.5k (copied: frame 190's
closing line, `plans/archive/stack-2026-10-10.md`). Meta workflow.

| Item | Tokens |
|---|---|
| the design so far, 290.5k, the review, 183.0k, and this section, about 80k | about 550k |
| a review of this section on Opus | about 120k |
| pass 1 and its diff review | about 120k and 90k |
| pass 2 and its diff review | about 380k and 220k |
| fix passes and delta reviews, on frame 190's two runs of about 230k | about 500k |
| the night read | about 350k |
| the case re-records, GPU apart | none in tokens |

Total in agents: about 2.3M to 2.5M, the review's figure.

Status 2026-10-10 04:35: section 2.F written by the Opus agent of session
45fc3fe2 on its resume, read-only on the tree at 43461f47, no model call,
not committed. Rota workflow, except 2.F.10's pass lines and 2.F.11, which
are meta workflow.

## 3. The tests

Each test rebuilds its rows inline, as `tests/rota/test_desk_guards.py`
does with `_night_rows` and `tests/rota/test_request_page.py` does for
frame 190. The night databases are ignored by git.

| Change | Case | Real turn | Kind |
|---|---|---|---|
| 2.1 | `pending_asks` hides m161 after m_p3, `frontier` closes it once s3 exists, and s299's staged ruling goes stale | night 137, s293 | `pending_asks`, `frontier`, `apply_rulings` |
| 2.1 | a request read as a question closes nothing, and m161 comes back | night 137, m_p3 with no statement | `pending_asks` |
| 2.2 | the boundary parks the contested confirm item and not `echo_json`, and `contested`, `quarantined`, `grouping` and `signoff` skip it | night 137, s313's dispatch | predicates, `close_pages_before_request` |
| 2.2 | the agenda skips a row about a parked item and orders the current request's rows first | night 137, s290's 7 rows with the confirm item parked | `tick_agenda` |
| 2.3 | m192 numbers the version item, one waiting line, and no confirm or `echo_json` line, and "ok" leaves the confirm item as it was | night 137, m192's refs | `render_page`, `land` |
| 2.3 | a contest of another request's line is refused with the line named | night 137, s299's map on a page that numbers the confirm item | `rulings_rule` |
| 2.4 | the grouping offers no ticket of the contested confirm item, and offers it once approved | night 137, s321's dispatch | `grouping` |
| 2.4 | `batches.group` on the contested item is refused | night 137, s321's call | sandbox, `batches_group` |
| 2.5 | `later` on the confirm ticket parks the item, writes no approval and relays nothing | night 133, s481 on m350 | `rulings_rule`, `land` |
| 2.5 | `drop` lands as `contest` | night 137, s159 on m63 | `rulings_rule` |
| 2.5 | `ask` is refused with the call named, and the named call is admitted | night 137, s291 on m162 | `rulings_rule` |
| 2.5 | `resume` on the waiting line returns the parked contested item to the Vision Keeper's wake | night 137, the m192 case of 2.3 | `land`, `contested` |

**Unit tests that assert the old behaviour.** The implementer runs
`python -m rota.tools.map fn pending_asks`, `fn request_rows`, `fn
open_requests` and `fn grouping` first, and greps the tests for "is not a
ruling. Each line takes". `tests/rota/test_request_page.py` asserts the
open requests of a page. `tests/rota/test_grouping_rule.py` and
`tests/rota/test_predicates.py` build grouping fixtures that may hold a
draft item. Each rewrite keeps the test's intent.

## 4. The risks

**What a seat sees differently.**

- The principal: a page sent before a request is gone from the next read.
  A page of the new request carries one waiting line per parked item. An
  approved earlier request's owed park page still comes.
- The Liaison in `landing` and `answering`: two new words in the brief,
  `later` and `resume`, and three new refusals. The `drop`, `ask` and
  unknown-word refusals change their text.
- The Architect in `grouping`: fewer wakes. One new refusal.
- The Vision Keeper: no `contested` wake and no `signoff` wake on a
  parked item.

**Which briefs change.** `rota/roles/prompts/liaison/landing.md` and
`rota/roles/prompts/liaison/answering.md`, two lines each. No other brief.

**Which cassette cases go stale** (reasoned: the case ids of
`tests/rota/cases/*.yaml`, read by grep, 2026-10-10). The gate prints the
stale set on its five lines, and decides.

- The 7 `l1_landing.yaml` cases, because `landing.md` changes. Re-record.
- `L1-LI-a-reply-reaches-the-desk-that-asked` (`l1_answering.yaml:9`),
  because `answering.md` changes. Re-record.
- `L1-AR-group-into-batches` (`l1_judgement.yaml:277`): its fixture item is
  `approved` at version 1, so the new door admits its calls. No change
  expected.
- The present and sign-off cases, `L1-LI-present-for-signoff`,
  `L1-LI-present-carries-the-uncovered-statement`,
  `L1-LI-surface-a-quarantined-message` and the park cases of
  `l1_liaison2.yaml`: their fixtures hold one request, so `render_page` is
  unchanged for them. No change expected.
- Two new cases, recorded at 5 runs each.
  `L1-LI-a-separate-request-is-put-aside` replays s481's turn on m350 in
  `answering` and expects one `rulings` write whose map holds `park` for
  the confirm ticket's item and no contest. `L1-LI-a-dropped-line-is-a-contest`
  replays s159's turn on m63 and expects `contest` on lines 2 to 8.
- The scenes. `two_batches` (`rota/testkit/scenes.py:638`) says item 2
  while item 1 is approved and its batch is deferred: 2.2 parks nothing
  approved, so the preempt and the park page stand (reasoned: the scene's
  docstring and 2.2's rule). `merged_then_next` says item 2 after item 1
  merged: nothing parks. Both scenes may still read a closed page if one is
  open at the second `say`. The scene tests decide.

**Two behaviours a night may show.**

- An approved earlier request keeps building, and its own owed pages
  reach the principal while the principal works on the new request. The
  principal may answer "for later", which now parks it. These pages count
  in the first ratio of the frame's ends-when, "pages that carry a request
  the principal has moved past". Night 137's walk 2 ended with the confirm
  item `approved` and `batch_1_confirm_eof_default` `pending` after both
  ladders were exhausted (copied: `plans/night137-read.md`, section 4), so
  one exhausted-ladder page about it is likely in walk 3 (reasoned: the
  ladder climbs to the Liaison).
- A parked item stays parked when the current request merges. The
  principal resumes it by a ruling or by asking for it again.

## 5. The open questions

Each question was checked against `rota/LAWS.md`, `rota/DECISIONS.md`,
`plans/composition.md` and the Liaison's briefs. A question the records
answer is not asked, and its answer is written here with its record.

**Answered by the records, not asked.**

- Does a new request park an approved earlier request that is building?
  No. The composition, Flows: "Only a ratified amendment to something
  approved revokes work downstream." A new request is not an amendment of
  the earlier item. Law 9 orders the two by priority. Roman's shape names
  merged, contested and draft, and the composition settles the fourth
  state.
- Does an approved earlier request's park page still reach the principal?
  Yes. "A given-up batch put back in the chair waits for the principal"
  (ruled: Roman, 2026-09-27, `scheduler.parked`), and the page goes when a
  criterion's own test is red (DECISIONS, 2026-10-08, point 3).
- Does the door write the sentence of a question back for `ask`? No. The
  Liaison originates a question, and it names the row (the composition,
  the Liaison). `landing.md`: "Answer it from the page and `line_rows`, in
  your own sentence." So the door refuses and names the call.

**Open.**

1. **[med] Does a request also close an open onboarding page, sent before
   any request?** Night 137's m62 was an onboarding agenda page, still open
   at walk 1's start, and the principal answered "Line 1 only describes
   what Click is" (copied: `plans/night137-read.md`, section 1). Roman's
   point 1 names pages "of an earlier request", and an onboarding page
   belongs to no request. The records hold no ruling on it. Recommended:
   yes, every open page with a lower `seq` closes, because the rule then
   reads one fact, and frame 41's wall shows the page answered out of
   place. Its ledger rows stay open and reach a later page.
2. **[med] How does the principal take a parked request up again?**
   No record covers an item park, because none exists (section 1.4).
   Recommended: the waiting line is numbered, and the Liaison rules it
   `resume` when the principal writes "reopen", "resume" or "take it up
   again". A resume returns the item to the state it held, and does not
   park the current request, because the composition revokes nothing
   without an amendment. The alternative is a new request that names the
   item, which makes a second item from the same words.
3. **[low] The waiting line's words.** Recommended: "<item text>. You put
   this aside when you asked for the change above. To take it up again,
   say reopen line <n>." The answer sets a sentence and no edit depends on
   it.

## 6. The passes and the price

The prices come from frame 190's actuals in its closing line,
`plans/archive/stack-2026-10-10.md`: design 361.7k, design review 152.2k,
the three designed passes 291.1k, 307.3k and 196.9k, five fix passes of
47.2k, 25.2k, 93.7k, 46.0k and 21.5k, reviews of 132.7k, 145.4k, 213.8k
and 149.1k for the designed passes and 68.0k to 7.9k for the deltas, and
a night read of 353.5k. About 2.86M in agents against an estimate of about
1.23M. Meta workflow.

**Two passes**, one implementer on Opus resumed by message, because both
passes touch `principal.py`, `api.py` and `predicates.py`.

- **A design review on Opus**, on this record before any code: about 150k.
- **Pass 1, the boundary, the park and the page: 2.1, 2.2 and 2.3.**
  Files: `rota/roles/principal.py` (`current_request`, `request_of`,
  `page_request`, `pending_asks`, `open_requests`, `request_rows`,
  `request_block`, `render_page`, `render_state`, `land`),
  `rota/core/scheduler.py` (`close_pages_before_request`, `not_parked`,
  `frontier`, `tick_signoff`, `tick_slicing`, `tick_criteria`,
  `next_batch`, `tick_agenda`), `rota/core/predicates.py` (`contested`,
  `grouping`'s park filter, `preempt`, `park_ask`, `touch_note`,
  `quarantined`), `rota/core/schema.sql` (`item_parks`), `rota/roles/api.py`
  (`rulings_rule`'s other-request refusal), and the tests of 2.1 to 2.3.
  About 300k to 340k for the implementer, on 291.1k and 307.3k, and about
  150k to 210k for its diff review. Re-records, GPU apart: none expected.
  The scene tests run. It lands first, because 2.5's `park` and `resume`
  write the table that pass 1 builds.
- **Pass 2, the words and the grouping: 2.4 and 2.5.** Files:
  `rota/roles/api.py` (`RULING_WORDS`, `rulings_rule`, `batches_group`),
  `rota/roles/principal.py` (`land`'s `park` and `resume`),
  `rota/core/predicates.py` (`grouping`'s approval condition), the briefs
  `liaison/landing.md` and `liaison/answering.md`, the tests of 2.4 and
  2.5, and the two new cases. About 150k to 200k for the implementer, on
  frame 190's pass 3 at 196.9k, and about 130k for its diff review.
  Re-records: the 7 landing cases, the answering case, and the two new
  cases at 5 runs each.
- **Fix passes after the reviews.** Frame 190 ran five, 234k in all, and
  five delta reviews of about 230k. Expect about 150k and 150k here.
- **One night as the walk**, three requests, with the read on Opus at
  about 350k. The read counts the three ratios of the ends-when and the
  residue.

Total in agents: about 1.5M to 1.8M, against frame 190's 2.86M for three
designed passes and five fix passes.

Status 2026-10-10 04:09: written by an Opus agent of session 45fc3fe2,
read-only on the tree at 43461f47, no model call, not committed. Rota
workflow, except sections 1.1's walk facts and 6, which are meta
workflow.

### 2.G Amendment from night 138: the precondition of the shift question

Written by session 4b501a17 on 2026-10-10, from the read of night 138's two
request boundaries and the interviews of s270 and s353 in their contexts
(`plans/frame193-interviews.md`). Rota workflow, except the status lines,
which are meta workflow.

**What the night showed** (observed: night 138, walks 2 and 3, 2026-10-10
12:14 to 12:36). The shift question of 2.F.1 fires when the new request has
a statement. On both boundaries no such statement formed. On walk 2 the
Liaison s270 read the new words in `principal_said`, confirmed the earlier
statement s1 with `msg.confirm_principal`, and segmented nothing. On walk 3
the Liaison s353 segmented the new words with `supersedes='s1'`, and 2.F.6
then made the new request a follow-up of the earlier one. In both, the
mechanism of 2.F never ran: 0 shift pages, 0 parks, 14 pages of request A
to the principal after the principal said "two separate changes". Verdict
mode then ratified the contested s1 again and delivered it (s273).

**What the seats said** (observed: the interviews, 2026-10-10 12:44). Both
seats said that s1 and the new words name different functions. s270 named
`current_request` naming s1 and a `recent_chat` about echo_json as the
inputs that tied the new words to s1, and said a wake without s1 in
`current_request` would have led it to segment. s353 said it compared the
new words to the brief's `version_option` example, not to s1, and named
`current_request` naming s1 as well.

**The amendment.** Four changes. Each is small, and each closes one path
that night 138 took around the shift question.

- **2.G.1 The wake says what `current_request` is.** The converse wake's
  `current_request` block gains a field `relation`, a sentence: "This is
  the request before these words. The new words continue it only when they
  name the same function or the same feature. Otherwise they are a new
  request, and you leave `supersedes` out." The brief's `supersedes`
  paragraph changes its example subject to one no night request uses
  (`--color` and `--quiet` flags, not `version_option`, `echo_json`,
  `confirm`), and gains the opposite example in the same sentence shape:
  "After a request about `echo`, 'let confirm take a flag' names another
  function, so it is a new request with no `supersedes`." (reasoned: the
  interviews named these two inputs three times each.)

- **2.G.2 The confirm door reads the trigger entry.** `msg.confirm_principal`
  on a converse wake whose trigger is a principal entry refuses when no
  statement, staged or stored, spans that entry, and every ref names a
  statement from another entry. The refusal names the entry and says:
  "The words that woke you, `e_p2`, have no statement. Segment them with
  `brief.segment` and confirm that statement. If they ask for nothing, call
  no confirm." One sentence, one call named. (reasoned: s270's miss is
  exactly a confirm with refs from another entry.)

- **2.G.3 Verdict mode has a contest branch.** The verdict brief gains one
  paragraph: a statement the principal contested is not ratified and not
  delivered. The seat ends the session with no call when every statement
  on the page is contested. The principal's reply is already recorded as an
  entry, and the converse wake on it segments the restated words. The
  `brief.ratify` door refuses a statement whose newest ruling is `contest`,
  with the ruling id named. (reasoned: s273's prompt held
  `principal_verdict: {s1: contest}` and the brief had two steps and no
  branch.)

- **2.G.4 `ratified_request` skips a statement the principal called
  separate.** When the newest landed ruling on a confirm page of statement
  X is `contest`, the wake offers no `current_request` with X. The seat
  then sees the field absent, and the brief's last sentence applies: leave
  `supersedes` out. (reasoned: on walk 3 the wake offered s1 after m138's
  contest, and the seat copied it.)

**What stays.** The predicate 2.F.1 keeps its precondition. A backstop that
fires the shift question on a request with no statement was considered and
left out: the fix above makes the statement form, and a shift page built
from an entry's raw words would name no statement for the ruling to land
on. A door on `brief.segment` that refuses `supersedes` when the two texts
share no identifier was considered and left out as a candidate: a
follow-up phrased without the function's name would be refused. Both return
as frames if a night shows the need.

**Tests.** One recorded case per change on the Liaison: the confirm door's
refusal on s270's shape, the verdict contest branch on s273's shape with
the ratify door, the segment with no `supersedes` on s353's shape with the
new wake field, and `ratified_request` returning None after a contest. The
touched existing cases re-record.

**Ends-when, unchanged.** The three ratios of the frame's ends-when, on a
night with three requests. Night 138 is the baseline: 0 of 2 boundaries
fired the shift question.

#### 2.G.5 to 2.G.7, from pass 3's measurement

Pass 3 built 2.G.1 to 2.G.4 and recorded three cases at 5 runs
(observed: the implementer's report, 2026-10-10 15:15). The s270 case
passed 5 of 5 with the confirm door. The s353 case, a new request about
another function with `current_request` present and no contest, passed 3
of 5: in two runs the seat set `supersedes` to the earlier statement with
the `relation` sentence and the new example in front of it. The s273 case
passed 0 of 5: the seat called `brief.ratify` first in every run, the door
refused it, and in three runs the seat then delivered the contested
statement to the three desks. Two conclusions (reasoned: from the counts):
the brief alone does not hold `supersedes` off a separate request, and a
door on one call does not stop the next call.

- **2.G.5 The `supersedes` door.** `brief.segment` with `supersedes`
  refuses when the new text and the superseded statement's text share no
  content word. A content word is a word of four letters or more, lower
  case, after a split on every character that is not a letter or a digit,
  with `_` as a split character too, minus a stoplist of English function
  words (that, this, with, when, then, also, into, from, have, make, take,
  give, should, would, there, their, which, where, what, does, them, they,
  only, just, like, same, next, more, than, some, each, every, over, after,
  before, instead, please). The refusal: "`supersedes` names `s1`, and the
  new words share no word with it. A follow-up names the function or the
  feature it continues. Leave `supersedes` out when the words are about
  another function." The failure mode of this door is one extra question:
  a follow-up refused in error becomes a new request, the shift question
  fires, and the principal says which request is current. The failure
  mode of the brief alone is a separate request merged into the earlier
  one in silence, and the mechanism never runs. Roman's ruling of 04:33
  prefers the question (reasoned). This reverses the "left out" line
  above for this door, on the measurement.
  Pass 3c: the stoplist also holds flag, option, options, helper, function, change, changes, request, message, output, value, values, default, command, line, lines, user, users, file, files, and no second rule is needed: 0 wrong admits of 10 pairs on nights 133 to 138 (3 before, all on "flag"), the night 138 pair refused, the brief's follow-up pair admitted on "show" and "version" (observed: the reviewer's probe, 2026-10-10).

- **2.G.6 The deliver door in verdict mode.** `msg.deliver_vision_keeper`,
  `msg.deliver_terminologist` and `msg.deliver_architect` refuse a
  statement that `contested_statement` marks, with the ruling id named,
  in the same words as the `brief.ratify` door. The s273 case measures
  effects and not calls: no statement ratified again and no delivery
  landed. A refused call is the door at work.

- **2.G.7 The sentence on the restated words.** 2.G.3 said that the
  converse wake on the principal's reply segments the restated words. The
  reply to a confirm page wakes `landing`, not `converse`
  (`_mode_key` in `rota/core/runner.py`, the branch on `cause_verb` in
  `confirm` and `present`), and `landing` has no `brief.segment`. So no
  path segments a restatement that arrives as a contest on a confirm
  page. The verdict brief's sentence changes to: "The principal's reply
  is already recorded as an entry. Nothing in this mode segments it." The
  path itself is left open here: with 2.G.2 in place the first confirm
  names the right entry, so the contest with a restatement is the rare
  case, and a night that shows it pushes a frame.
