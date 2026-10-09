# Frame 190, what the principal sees: the scope and the design

Status: written by an Opus agent of session d7cf65d1 on 2026-10-09 at
about 10:48, before any code, read-only on the tree at 2511355a. The tree
at 07c9599c differs from 2511355a only by records (observed: `git diff
--stat 2511355a HEAD -- rota tests probes` is empty, 2026-10-09 10:48).
Night 136 ran at 40691aa7, which differs from the tree only by records
(copied: the brief of this agent). Both workflows. Each line names its
workflow where the two differ. The night facts come from
`.rota/clickI_night136.db` and `.rota/clickI_night133.db`, read with
`mode=ro&immutable=1` by the scripts `p2.py` to `p9.py` in the scratchpad
folder `d190` of session d7cf65d1, and by `acts.py` and `loop1.py` in the
folder `n136` of session 7d45e193.

Verdicts, one line each:

- 49 of night 136's 60 presents are `agenda` pages, and all 49 carry no
  line of the request. On night 133, 27 of 46 presents are `agenda`
  pages, and all 27 carry no line of the request. Section 1.2.
- 117 of the 213 ledger lines on night 136's agenda pages are rows that a
  seat wrote in a session woken by a relay of a principal verdict, about
  a row that relay named. 31 of the 49 agenda pages hold only such rows.
  Night 133: 67 of 154 lines, 7 of 27 pages. Section 1.4.
- No page of night 136's walk 3 loop carried the item that the principal's
  words named, so no ruling could land on it. Section 1.3.
- A `revise` on an item lands no words on the item. `_resolve_contest`
  reads `contest` only, and on night 136 the Vision Keeper's relay session
  s172 set the revised item `approved`. Section 1.5.
- The touch note shows the item and the predicted files, and no criterion.
  The quarantined page m96 did not say that cr_3 has no test. Section 1.6.
- The blindspot session s87 wrote 56 ledger rows whose words are one label,
  `prose`, `surface`, `term` or `source`, on both nights. 16 of them
  reached night 136's pages. Section 1.7.
- Five changes, section 2: the request's own lines first on every page,
  one route from the principal's words to the item, the Architect's reply
  that writes no new row, the next page that is not a seat's reply row,
  and the touch note that names a criterion with no test.

## 1. The scope report

Rota workflow throughout, except where a line says meta workflow.

### 1.1 How a page is built

**`render_page`** (`rota/roles/principal.py:495-664`) turns a message's
verb and refs into the page text and the order of its numbered rows. The
page is built from rows at each read. The five callers:

| Caller | Line | What it renders |
|---|---|---|
| `runner.resolve_inbound` | `runner.py:1604` | the page in the Liaison's `landing` working set |
| `api.rulings_rule` | `api.py:6919` | the order a ruling's line numbers map to |
| `api.rulings_line` | `api.py:7070` | the row behind one line |
| `principal.pending_asks` | `principal.py:177` | every open ask to the principal, for `pump` and the state page |
| `principal.render_ask` | `principal.py:367` | the page alone, no `ask_id`, for two test files |

`pending_asks` (`principal.py:168-185`) lists every open message to the
principal whose verb is not `converse`, ordered by `seq`. `render_ask`
(`principal.py:364-367`) returns the first half of `render_page`.

**The branches of `render_page`.** A park message (`park_ask_batch(ask_id)`)
goes to `_park_page` (`principal.py:435-492`), frame 142's page: "You
asked:" with the item, "It must:" with each criterion and its `check:`
line from `check_line` (`principal.py:394-432`), then the last attempt.
Every other present sorts each ref into one group (`principal.py:535-576`):

| Group | Rule | Heading on a present |
|---|---|---|
| `said` | a statement row (no `approval`, a status) | "You asked:" |
| `account` | the item `how_it_works` | "What we are building:" |
| `described` | an item with `is_description` | "How it is described:" |
| `does_today` | an in-scope item with provenance `observed` | "It does today:" |
| `does` | any other in-scope item | "It would:" |
| `does_not` | an out-of-scope item | "It would not:" |
| `assumed` | a row with `default_taken`, a ledger row | "Where you did not say, I assumed:" |
| `terms` | a glossary row | "A word that means more than one thing here:" |
| `touches` | a ref that no table resolves and that `touch_words` reads, a batch | numbered, after the item, on the touch note |
| `other` | any other row with text, such as a criterion or a constraint | numbered last, with no heading |

The touch-note branch (`principal.py:596-604`) fires when a present holds
a batch ref. It numbers `does + account`, then the batch line from
`touch_words` (`principal.py:761-782`): "the work for: <item text>;
expected to touch <paths>; might touch <symbols>". The general present
branch (`principal.py:612-648`) numbers the groups in the order of the
table. A criterion has no group of its own. It falls to `other`, with no
heading, after every assumption.

**Where the request's own text is.** The principal's words are the entries
`e_p1` to `e_p3`. `brief.segment` cut each into one statement, s1 to s3,
`ratified`. Each in-scope item cites its statement through `refs` with kind
`statement` (observed: night 136, `refs` rows `items/echo_json -> s1`,
`items/confirm_with_default_on_eof -> s2`,
`items/version_option_show_python -> s3`, 2026-10-09). Each item has one
ticket, `tk_1_<item>`, and the Terminologist's criteria hang from the
ticket (observed: `batch_tickets` joined to `criteria`, night 136: bg_4
holds `c1_version_option_show_python` to `c3_version_option_show_python`).

The request's text reaches a page only when a ref of the page is the
statement or the item. The sign-off page carries both, because the door
adds the uncovered statements and the lineage's assumptions to a present
caused by a `submit` (`sandbox.py:2370-2420`). The touch note carries the
item, because `touch_note` wakes with the batch and the item. The park
page carries the item and its criteria. The `agenda` page carries only
open ledger rows, `observed_entries` only observed rows, and the
quarantined page only the batch, item or ticket of a dead key. No page
except the park page shows a criterion with a heading.

**What a line's ref is.** The `order` list holds the row id behind each
numbered line. `rulings.rule` maps a line number to that id
(`api.py:6965-6966`). The id names a row of `statements`, `items`,
`criteria`, `ledger`, `glossary_terms`, `constraints`, `model_areas`, or
a batch id. `rulings.line` returns the row and its table
(`api.py:7083-7088`).

### 1.2 Who sends a page

Seven Liaison modes hold `msg.present_principal` in their `.tools`:
`agenda`, `observed_entries`, `park_ask`, `quarantined`, `round_close`,
`submit` and `touch_note` (observed: `grep -l present_principal
rota/roles/prompts/liaison/*.tools`, 2026-10-09). Two modes write a
principal message through `rulings.rule(ask=...)`: `landing` and
`answering`.

| Mode | Wakes on | Band | What the refs are |
|---|---|---|---|
| `submit` | a Vision Keeper `submit` message | traffic | every item, the uncovered statements and the lineage's open assumptions, added by the door (`sandbox.py:2370-2420`) |
| `agenda` | `agenda` (`predicates.py:1571`), through `tick_agenda` (`scheduler.py:931-972`) | gate | the oldest seven open ledger rows by `rowid`, the wake's refs, added by the door (`sandbox.py:2365-2367`) |
| `observed_entries` | `observed_entries` (`predicates.py:545-668`) | start | every code-observed row not yet on a present |
| `touch_note` | `touch_note` (`predicates.py:770-801`) | start | the batch and its item |
| `quarantined` | `quarantined` (`predicates.py:1457-1530`) | fix | the batch, item or ticket of each quarantined key, less a key that a park owns |
| `park_ask` | `park_ask` (`predicates.py:1532-1568`) | fix | the door writes the item and the criteria, or the batch for a note |
| `round_close` | `round_close` | gate | the reports' rows |

**`tick_agenda`** returns nothing while a message other than a touch note
is open to the principal (`scheduler.py:952-956`). Otherwise it returns one
wake while any ledger row is `open`, with the oldest `PAGE_ASSUMPTIONS`
rows, seven, as refs (`scheduler.py:958-972`). It reads no author, no
`about_ref` and no request. The `agenda.md` brief says: "Put them on one
page with one `msg.present_principal` whose refs are the ledger rows' own
`id`s". The door refuses more than seven open rows on one page
(`sandbox.py:1913-1923`).

**The band order** (`predicates.py:71-76`): traffic 0, fix 10, gate 20,
start 30. Within a band the file order decides (`predicates.py:87-93`).
`agenda` is band `gate`. `annotate` (`predicates.py:753-767`), `touch_note`
and `batch_start` are band `start`. The `agenda` docstring gives the
reason for band `gate`: the Critic's challenge ticks in band `start` each
wrote one ledger row, and the agenda outranked them, so every row raised
its own page (tipsV, 2026-09-09). The fix for that was the onboarding gate,
`onboarding_phase(conn) not in ("done", "none")`, and the band stayed.

**The pages of both nights, by the mode that sent them** (observed:
`p6.py`, 2026-10-09). A request line is a statement, a criterion, or an
item that is not `observed`.

| Mode | Night 136 presents | No request line | Night 133 presents | No request line |
|---|---|---|---|---|
| `agenda` | 49 | 49 | 27 | 27 |
| `submit` | 3 | 1 | 8 | 2 |
| `touch_note` | 3 | 0 | 4 | 0 |
| `quarantined` | 3 | 1 | 4 | 2 |
| `observed_entries` | 1 | 1 | 1 | 1 |
| not joined to a session | 1 | 0 | 2 | 2 |
| all | 60 | 52 | 46 | 34 |

**Night 136's bg_4.** bg_4 was grouped by s514. After s514 the only ticks
were `observed_entries` once and `agenda` 13 times. Each round left one
open ledger row, so `agenda` fired every round and `annotate` never ran.
bg_4 has no `batch_touch` row and stayed `pending` (copied:
`plans/night136-read.md`, section 2, 2026-10-09).

### 1.3 Where a ruling's words go

**`rulings.rule`** (`api.py:6861-7041`) is the `landing` mode's one write.
It maps each line number to the row in `order`, needs a ruling on every
line (`api.py:6996-7002`), and needs `words` for any contest or revise
(`api.py:7010-7013`). It stages one `rulings` row. `apply_rulings`
(`principal.py:1028-1060`) lands the row through `land` after the session
commits. `revise` takes no new text. The words of the reply ride in
`words` for every line alike.

**The batch-line door of frame 142's step 2.D** (`api.py:6978-6995`)
refuses a contest or a revise on a ref that is a batch, on every page: "<batch>
is the change's line: a prediction of what it touches, and a ruling on it
moves nothing. To stop the change, contest the item <item>, line <n>.
Otherwise approve the line".

**`land`** (`principal.py:806-1025`), what each ruling does:

| Line's ref | approve | contest | revise |
|---|---|---|---|
| an item | `UPDATE items SET approval='approved', approval_ver=version` (`principal.py:955-964`), on every page | `approval='contested'` | `approval='contested'`, the same write |
| a ledger row (`open`) | a decision under the principal's name, "default taken at signoff", and the row `resolved` (`principal.py:909-938`) | a decision "overruled at signoff: <words>", the row `resolved`, and its `about_ref` contested, unless the `about_ref` is an observed item (`principal.py:928-932`) | the same as contest |
| a batch | dropped from the ruling (`principal.py:877-882`). A page all approve closes and wakes nobody | refused before `land` by the batch-line door | refused before `land` |
| a criterion, constraint, term or area | no state write here | no state write here. The verdict relays it | no state write here |

The verdict message goes to the Liaison `open` with the ruled refs less
the closed ledger rows, and `config` holds `verdict:<id>` with the map
(`principal.py:983-1000`). The Liaison wakes in `verdict_signoff`
(`runner.py:206-212`). Its brief relays items to the Vision Keeper, terms to
the Terminologist, and constraints and areas to the Architect. The door
routes each ref by ownership: `_owner_of_ref` (`sandbox.py:848-859`) looks
up `RULED_TABLES` (`sandbox.py:839-845`), and a ledger id goes to its
`author`. A criterion goes to the Terminologist only on a park page
(`sandbox.py:2651-2676`).

**Why a contest on a constraint row reaches the Architect and never the
item.** On night 136's walk 3 every page from m391 held one ledger row of
kind `default`, by the Architect, about the constraint
`parametersource_commandline` (observed: `p3.py`, the 12 rows of the loop,
2026-10-09). A contest of that row closes the row and contests its
`about_ref`, the constraint. `_owner_of_ref` gives the Architect. No ref
of the page reaches the item `version_option_show_python`, so no part of
the route names it. The item was approved at version 4 (observed:
`items`, night 136).

**The round of s557 to s560** (observed: `acts.py`, 2026-10-09):

1. s557, `landing`, on m420: `rulings.rule(rulings={1: "revise"},
   words="... Please replace line one with exactly this: a new show python
   flag on the version option ...")`. The ruling lands on the ledger row.
2. s558, `verdict_signoff`: `msg.relay_architect(["parametersource_commandline"])`,
   m422.
3. s559, Architect `relay`: its prompt holds `principal_verdict:
   {"parametersource_commandline": "contest"}` and the principal's words
   whole as `principal_said`. It calls `ledger.log(about_ref=
   "parametersource_commandline", about_table="constraints",
   assumption="The principal's contest on parametersource_commandline
   requires a refactor to align with the new show python flag
   behavior.")`, which lands as `l_758e5d392a`, then
   `model.adopt(ids="parametersource_commandline")` three times. Each
   call is refused: `'p' is not a row of model_areas`.
4. s560, `tick:agenda` with `ledger=1`: `msg.present_principal(refs=
   ["l_758e5d392a"])`, the next page.

The first session that read the exact line is s537, on m400, the answer to
m399. It ruled `{"1": "contest"}` with the words whole. s538 relayed the
constraint. s539 logged `l_ea8c74fa6a` and failed `model.adopt` three times
in the same way (observed: `acts.py`).

**The five corrections of a predicted file** (observed: `acts.py` on s185,
and `plans/night136-read.md`, section 1). Page m84 numbered the item as
line 1 and the batch line as line 2: "expected to touch
src/click/termui.py, tests/test_defaults.py; might touch
test_lookup_default_override_respected". m85 said "Line 2 names the wrong
tests: the confirm prompt's tests live in the terminal UI test file". s185
sent `rulings.rule(rulings={"1": "approve", "2": "contest"}, words=...)`
three times. The batch-line door refused each, and the runner ended the
session for a repeat. s201 on m97, s343 on m228, s361 on m237 and s368 on
m247 did the same. bg_2 ran from s186 (copied: `plans/night136-read.md`,
section 1).

### 1.4 What the Architect does with a relayed ruling

`_mode_key` (`runner.py:190-278`) keys a message wake by its verb, so a
`relay` to the Architect selects `architect/relay.md`. Its tools are
`model.adopt`, `model.load` and `ledger.log`. The brief says: "A
**contested** row is not yours to fix in this session. It stays observed,
on file as contested ... If the contest tells you an assumption you made,
`ledger.log` it." Then: "Adopt, then stop."

So on a contest the one write the brief offers is a new ledger row.
`ledger.log` (`api.py:7102-7173`) refuses a row about a ledger row and a
row under the wrong table, and nothing else that applies here. The id is
a hash of the table, the ref and the words (`api.py:7201-7203`), so a
different sentence about the same constraint is a new open row. The row is
`open`, and `tick_agenda` presents any open row.

`model.adopt` (`api.py:1627-1644`) iterates `ids`. A string iterates by
character, so `ids="parametersource_commandline"` reads `p` first and
`_adopt_rows` refuses it. The relay held no approved id, so the call had
nothing to adopt in any form.

A relay is a message wake, so the runner's nudge for a session that ends
with nothing done does not apply (`runner.py:3247-3268` holds it to
`wake.kind.startswith("tick:")`). A relay session may end with no call.

**The seats' reply rows on the pages** (observed: `p7.py`, `p9.py`,
2026-10-09). A reply row is a ledger row written by a session woken by a
relay whose cause is a principal verdict, about a ref that relay named.

| Night | Ledger lines on pages | Reply rows | Agenda pages | Pages of reply rows only |
|---|---|---|---|---|
| 136 | 213 | 117 | 49 | 31 |
| 133 | 154 | 67 | 27 | 7 |

The writers of the lines on night 136's pages: Architect on a verdict
relay 98, Vision Keeper `reconcile` 47, Terminologist on a verdict relay
17, Liaison `blindspot` 16, Tester `tests_missing` 10, Vision Keeper
`deliver` after a verdict 7, and 18 others. Night 133: Architect on a
verdict relay 51, `reconcile` 47, Terminologist on a verdict relay 26,
`blindspot` 16, and 20 others (observed: `p7.py`).

### 1.5 What the Vision Keeper does with a ruling on an item

A contest of an item reaches the Vision Keeper twice. `verdict_signoff`
relays it, and the Vision Keeper's `relay` mode writes
`problem.set_approval` and `problem.prioritize`. `contested`
(`predicates.py:236-245`, band `fix`) wakes the Vision Keeper on
`tick:contested`. That wake's working set comes from `_resolve_contest`
(`runner.py:1712-1747`), which finds the newest `verdict:<id>` whose map
says `contest` for the item and adds `principal_said` and `entry_id`. The
`contested.md` brief then has two cases. When the words carry a
replacement, `problem.assert(id=<item>, text=<what they meant>)` amends
the item. `problem.assert` writes `approval: "draft"` (`api.py:1314`).

**A `revise` on an item carries no words to the item** (reasoned:
`runner.py:1731` matches `contest` only, so a map that says `revise`
returns `{}` and the Vision Keeper wakes with the item alone). On night 136
the ruling r_5869cf4c71 on m73 said `confirm_with_default_on_eof:
revise`, with the words "line 5 should say the new flag is off by
default". The relay session s172 then set that item `approved`, twice,
and the `tick:contested` session s173 worked on `echo_json` alone
(observed: `config` `verdict:m75` and the calls of s172 and s173,
2026-10-09). The revised item drew no amendment from that ruling.

**The version and the cancel.** `problem.assert` moves the item's
version and sets `draft`. `signoff` (band `gate`) submits it again.
`cancel` (`predicates.py:1336-1355`) abandons every live batch whose item
is not `approved` at its version. Night 133 lost bg_2 and bg_4 this way,
after s342 and s517 put the principal's correction on the item text
(copied: `plans/night133-read.md`, section 3, wall 4). After the new
approval, `tick_slicing` (`scheduler.py:248-305`) slices again only an
item that was delivered at an older version, or an item with no ticket.
An item amended before its delivery keeps its old ticket and its old
criteria, and `grouping` puts them in a new batch (reasoned: the `WHERE`
clause at `scheduler.py:270-287`). The Developer and the Tester then work
from criteria that do not hold the new words.

### 1.6 The touch note

`touch_note.md` sends one `msg.present_principal` with the batch and the
item. The working set holds `touch`, from `touch_set`
(`lifecycle.py:342`, read at `runner.py:1365-1372`): the item, the
expected paths, the possible symbols, the unsurveyed ground and the
commitments. The predicted files come from the Architect's `annotate`
session (`architect/annotate.md`), which calls `batches.annotate`
(`api.py:4708-4755`). That call adds `batch_touch` rows keyed
`<batch>:<grain>`. It never removes an earlier row.

The page numbers the item and the batch line and says "This is a
prediction, not a promise". It shows no criterion, so it can say nothing
about a criterion's test. At touch-note time the Tester has written no
test, because `tests_missing` waits for `head_commit`
(`predicates.py:675-718`).

The Tester chooses each test's path. `tester/tests_missing.md` says "Nobody
assigns them". bg_2's tests went to `tests/test_utils/test_confirm_eof.py`
and `tests/test_utils/test_confirm_eof_behavior.py`, and bg_3's the same,
while the touch set named `tests/test_defaults.py` and the principal named
the terminal UI test file (observed: `tests` and `batch_touch`, night 136).

**m96, the quarantined wake on bg_2.** s200 woke on `tick:quarantined`,
`1 abandoned: tests_missing for bg_2 (tester), 3 attempts`, and presented
`["bg_2"]`. A page whose only ref is a batch renders as the touch note. It
said "Before I build this, here is what I expect to touch" and named no
criterion. cr_3 had no test (observed: `sessions` and `tests`, night 136).

### 1.7 Frame 45's old site, `blindspot`

`blindspot` (`predicates.py:1726-1732`) runs `tick_blindspot`
(`scheduler.py:1100-1124`) once, last in onboarding. `blindspot.md` asks
for "one entry with `ledger.log`" per gap that matters, about an area, and
says "Say the actual thing". Frame 45's shape was five blindspot rows that
named a Critic verdict that no row held.

On both nights the one blindspot session, s87, called `ledger.log` 56
times with the same calls, and each `assumption` is one word, the gap's
label: `prose` 38 times, `surface` 3 times, `term` 13 times, `source`
once (observed: `tool_calls` of s87, nights 133 and 136). 16 of these rows
reached night 136's pages m132, m138 and m142, and 14 reached night 133's
pages. Night 133's m122 showed `term`, `source` and `term` as lines 1, 3,
4, 6 and 7. These are the words of frame 184's ask-backs, `surface` and
`prose` (copied: `plans/night133-read.md`, section 2). Night 136 shows no
row that names a verdict, frame 45's own shape.

### 1.8 The three shapes at each site

| Site | Shape 1, walk 3 loop, night 136 | Shape 2, the prediction page, night 136 | Shape 3, whole-page contests, night 133 |
|---|---|---|---|
| `render_page` | m391 to m431 hold one ledger line and no item line | m84 and m227 number the batch line, m96 shows no criterion | m122 and the 15 others hold seven seat rows and no request line |
| `tick_agenda`, `ORDER` | s560 and 10 others present the newest reply row. `annotate` for bg_4 never runs | none | s228 and the others present the oldest open rows, blindspot and Architect rows first |
| `rulings.rule` | s537 contests and s557 revises the ledger line. Nothing reaches the item | s185, s201, s343, s361, s368 refused by the batch-line door | s229 asks back. s230 contests seven lines |
| `land`, `_owner_of_ref` | the constraint is contested and relayed to the Architect | not reached | the contested rows' `about_ref`s go to their owners |
| Architect `relay` | s539, s559 and 9 others log a new row and fail `model.adopt` | none | 51 reply rows on night 133's pages |
| Vision Keeper | not reached: the item is never ruled | not reached | not reached on these rounds |
| touch note | bg_4 gets none | m96 says nothing of cr_3 | none |
| `blindspot` | none | none | m122's lines 1, 3, 4, 6 and 7 |

## 2. The design

Five changes, one per mechanism. Each says its mechanism, its file and
function, its door or brief words, and one test on a real turn. Rota
workflow, except where a line says meta workflow.

The changes rest on these records. Law 8: "A lineage's open assumptions
are presented at its gates: nothing ships whose assumptions the principal
never saw." The ruling of 2026-09-03 (`rota/DECISIONS.md`, "The seed
interview runs at intent-time"): approve takes the default, and "contest
with words goes back to the desk that assumed it". The ruling of
2026-09-12 ("The seat's four pages are one surface"): "Nothing is asked
twice", and "An amended item cancels a running batch built from it and
re-batches". The ruling of 2026-09-13 ("The principal's flow", point 2):
"No batch starts until the first page is answered. After that, nothing
waits on a page." The ruling of 2026-10-08 ("The park ask is a page with
rows", point 4): "Every word of the principal is a ruling on a row, or it
earns one Liaison question that names a row." The composition: the
Liaison's question "names the row it is about", and the purpose, "no work
happens that the Principal did not ask for".

### 2.1 The page's lines: the request first, the team's notes after

**The mechanism.** Every present to the principal carries the request's
own rows, and the page numbers them first. The seats' rows follow under a
heading that marks them as the team's notes.

1. A new helper, `principal.request_rows(conn, refs) -> list[str]`,
   returns the request's rows for a page, in this order:
   - the items that the refs reach. An item ref is itself. A criterion
     reaches its ticket's item. A ticket reaches its item. A batch reaches
     `batches.item_id`. A statement reaches the items that cite it in
     `refs` with kind `statement`. A ledger row reaches what its
     `about_ref` reaches, one step. An observed item and the account
     `how_it_works` are not request items.
   - when the refs reach no item: the open requests. An open request is an
     in-scope item that cites a ratified statement, is not observed and
     not a description, and whose version is above its `delivered:<item>`
     config row, the rule `tick_slicing` already reads
     (`scheduler.py:279-286`). Ordered by `priority`, then id. At most
     three.
   - when there is no open request either: the account, `how_it_works`,
     the shape of an onboarding page before any request.
   - after each item, its criteria in id order, from `tickets` joined to
     `criteria`.
2. The send door, `_bind_send.stage` (`sandbox.py:2360-2420`), adds
   `request_rows(conn, refs)` to the refs of every `present` to the
   principal, added and never substituted, as it adds the wake's refs and
   the uncovered statements today. The page is still rendered from the
   message's refs on every read, so the order that `rulings.rule` reads is
   the order the principal read. The park message keeps the refs its own
   door writes (`park` branch), unchanged.
3. `render_page` (`principal.py:495-664`) gains one block that every
   present branch renders first. The block is the body of `_park_page`'s
   "You asked:" and "It must:" lines, moved into a helper
   `principal.request_block(conn, refs, order, out)`. Each criterion gets
   its `check:` line from `check_line`, or `check: none yet.` when no test
   row names it. `_park_page` calls the same helper, so the park page of
   frame 142 renders word for word as it landed.
4. After the block, the present branch numbers the other rows as today,
   under one heading: "The team's notes. A seat wrote each of these where
   your words were silent. They are not your request." The headings
   "Where you did not say, I assumed:" and "A word that means more than one
   thing here:" stay below it as sub-headings. The touch note's batch line
   moves under "The team expects to touch:".
5. The last line of a present gains one sentence: "To change what you
   asked for, name line 1." The line number is the first item's line.

**The request's own lines, by kind of page.**

| Page | The request's own lines |
|---|---|
| onboarding, before any request (submit, agenda, observed rows) | the account, `how_it_works`. No request exists yet |
| sign-off, a present caused by a `submit` | the statements and items, as today, and now the items' criteria when they exist |
| touch note | the batch's item and its criteria, each with `check: none yet.` |
| agenda | the items that the ledger rows reach, or the open requests, and their criteria |
| park page | the item and its criteria with their checks, frame 142's page, unchanged |
| quarantined wake | the item that the dead key's batch, item or ticket reaches, and its criteria with their checks (2.5) |

**When the only open rows are seat rows.** The page still goes, and its
first lines are the open request, or the account when no request is open.
The records answer whether it goes: law 8 presents a lineage's open
assumptions at its gates, and the ruling of 2026-09-03 makes the
principal's approve the one way a ledger row closes (law 11's note: "A
ledger entry is resolved by a decision that names it ... and by nothing
else"). A page of seat rows that never went would leave the rows open
forever. Change 2.4 removes the reply rows from the agenda's choice, and
change 2.3 stops most of them at the door, so the seat-only page is the
rarer case after this frame.

**What the page reads, for night 136's m399 as the new door sends it.**

```
Here is what I understand you want, on one page.
You asked:
  1. Give version_option a show_python flag that appends the running Python version to the message.
It must:
  2. When `version_option` is invoked, if the `show_python` flag is present, the output message must include the running Python version string.
     check: none yet.
  3. The `version_option` callable must accept a `show_python` boolean parameter that controls whether the Python version is appended.
     check: none yet.
  4. If `show_python` is false or absent, the output message must not include the running Python version string.
     check: none yet.
The team's notes. A seat wrote each of these where your words were silent. They are not your request.
Where you did not say, I assumed:
  5. The principal contested the constraint due to unclear requirements, and the approved line refers to a new show python flag on the version option.
Reply in your own words. 'ok' approves all of this and starts building. Name a line to correct only that line. Ask, if something here is unclear. To change what you asked for, name line 1.
```

**What the frames get.** Covers night 136's wall 4 and the page half of
wall 3, and night 133's wall 2. Covers frame 45's page half: the blindspot
rows go under the team's notes. Leaves frame 45's writer to 2.3. Frame 184
loses the source of its words when 2.3's door refuses a one-word row. Its
copy of `recent_chat` stays its own.

**The test.** Night 133, s228's dispatch and s229's turn on m122. Rebuild
inline the seven ledger rows of m122 with their authors, the item
`confirm_with_default_on_eof` at its night-133 version and approval, its
ticket and criteria, the statement s2, and bg_1 merged with
`delivered:echo_json`. `request_rows` on m122's refs returns the confirm
item and its criteria through the open-request rule, because no row
reaches an item. The door, on a scripted `msg.present_principal` with the
seven ids, writes a present whose refs hold the item and the criteria.
`render_page` numbers the item as line 1, the criteria next, and the seven
rows after "The team's notes". A ruling `{"1": "revise", <the seven
lines>: "contest"}` with m123's words is admitted.

### 2.2 The route to the item: one door, three kinds of line

**The door.** The principal's words land on the item through its own line
on the page, which 2.1 puts on every page. The Liaison rules that line in
`landing`, `rulings.rule` stages the ruling, and `land` writes it. Four
edits close the gaps that the three kinds of line show.

1. **A team's note takes no `revise`.** `rulings_rule` (`api.py:6861-7041`),
   after each key maps to a row: a `revise` on a ledger row, a constraint,
   a glossary term or a model area is refused when the page numbers a
   request item: "<line> is the team's note, not your request. revise
   rewrites a line of what the principal asked for, and that is line <n>,
   <item>. To put the principal's words on the request, revise line <n>.
   To drop the note, contest it." s557's `{1: "revise"}` on m419 would have
   read this refusal with the item named. A contest of a note keeps
   today's meaning: the note closes as overruled, with the words.
2. **A `revise` carries the words to the item.** `_resolve_contest`
   (`runner.py:1712-1747`) matches `contest` or `revise` for the item. The
   `tick:contested` wake then carries `principal_said` for a revise, and
   `contested.md`'s first case applies: "They said what they meant instead
   ... Amend the item and stop", with `problem.assert` on the item's own
   id. No brief changes. The words of `revise` are the reply's `words`,
   which `land` already stores as `entry:<verdict id>` and in the
   transcript (`principal.py:1001-1006`).
3. **An approve of a request line on a page that is not the sign-off
   page changes no state.** `land` (`principal.py:955-964`) writes
   `approved` on an item only when the page is the sign-off page, a
   present whose cause is a `submit` (observed: m2 and m73 on night 136
   are caused by `submit` messages), or when the item is observed. The
   item's approval belongs to the sign-off gate (law 8). Without this
   edit, an "ok" on an agenda page would approve a contested item that its
   owner has not yet amended, night 133's wall 5 shape. A contest or a
   revise lands on every page as today.
4. **The Vision Keeper's relay does not undo a ruling.**
   `problem.set_approval` (`problem_set_approval`, `api.py:1332-1339`)
   refuses, in a session woken by a relay of a
   principal verdict, a state other than the one `land` wrote for that
   item: "the principal ruled <item> <revise>. land wrote `contested`, and
   the contested wake carries the words. Leave it." s172's two
   `set_approval(approved)` calls on the revised confirm item would have
   read this refusal.

**How the door finds the item from the page's refs.** Through
`request_rows`, the rule of 2.1, at send time. The page's line 1 is the
item for a constraint row, a batch row and a predicted file alike, because
the door stamps it into the refs. `rulings.line("1")` returns the item's
row.

**What it writes, and what the Vision Keeper then does.** For s537's
words on the new m399: `land` sets `version_option_show_python`
`contested`, keeps `approval_ver`, and writes `verdict:<id>` as
`{"version_option_show_python": "revise", ...}`. `contested` wakes the
Vision Keeper with `principal_said`. It calls `problem.assert` with the
principal's line, the version moves to 5 and the approval to `draft`.
`cancel` abandons bg_4, which is `pending` and built from version 4, by the
ruling of 2026-09-12. `signoff` puts the amended item on the sign-off
page. After the approval, `grouping` opens a new batch on the same ticket
and criteria. Open question 5.1 asks whether the ticket and the criteria
are sliced again.

**A batch line and a predicted file: frame 142's batch-line door changes.**
A correction of a touch note's predicted files lands with the Architect,
who wrote the prediction, before the build.

1. `rulings_rule`'s batch-line door (`api.py:6978-6995`) admits a contest
   or a revise on a batch line when the batch has no head commit, the
   touch note before the build. It keeps the refusal for a batch with a
   head commit, with the item named, as frame 142 designed it for the
   quarantine page.
2. `land` (`principal.py:877-882`) keeps a batch ref with contest or
   revise in the verdict. An approve of a batch line is still dropped.
3. `RULED_TABLES` (`sandbox.py:839-845`) cannot hold a batch, because the
   relay split looks a ref up by table. `_owner_of_ref` gains one rule
   before its ledger lookup: a batch id goes to `architect`.
4. `_mode_key` (`runner.py:269-275`) keys an Architect `relay` whose refs
   hold a batch to the existing mode `annotate`. `annotate.tools` already
   holds `batches.annotate`. This is the shape of frame 142's
   `criterion_repair` key (amendment 4), for the same reason: a tool added
   to `relay` is an invitation (measured: `decisions.author` in a relay
   mode, 2026-09-03, the comment in `principal.land`).
5. `batches.annotate` (`api.py:4708-4755`), in a session woken by a relay
   of a principal verdict that names the batch, replaces the batch's
   `batch_touch` rows. The implementer proves the pipeline's delete on the
   case of section 3, or marks the old rows `confidence = 'withdrawn'` and
   `touch_set` skips them.
6. `architect/annotate.md` gains one paragraph:

   ```
   **A ruling of the principal.** When the message is a relay with
   `principal_verdict` on the batch, the principal read your prediction on the
   touch note and corrected it. The words are `principal_said`. Call
   `batches.annotate` once with the paths the words name, and keep every path
   they do not dispute. Then stop.
   ```

7. `verdict_signoff.md` gains one line in its table: "a batch —
   `msg.relay_architect`". The line about a criterion changes to "a
   criterion — `msg.relay_terminologist`", because 2.1 puts criteria on
   every page and the split already sends them there on a park page. The
   split (`sandbox.py:2651-2676`) drops the `on_park` condition for a
   criterion line, and keys the criteria apart from glossary terms, so a
   verdict with both sends two relays to the Terminologist: one keyed to
   `criterion_repair`, one to `relay`. `park_criterion_relay` widens to
   "a relay whose refs hold a criterion".

The Tester chooses where a test goes, and the Architect's corrected
prediction does not reach that choice. Open question 5.2 asks whether the
Tester's wake shows the batch's expected test paths.

**What the frames get.** Covers frame 189's mechanism half: a ruling on a
predicted file lands as a correction that the Architect reads before the
build. Covers night 136's walls 1, 3 and 4. Covers the inverted ruling of
night 136's wall 2 for the batch line (r_e3957b37f2, `bg_2: approve` after
the door), because the door no longer refuses the contest. Leaves frame
185, a put-off request, frame 186, the grouping on a contested item, and
frame 187, the contested tick, in their places. Covers frame 188's second
site only if a night shows no self-relay after 2.3. Its first site stays.

**The test.** Night 136, s537's turn on m400. Rebuild inline the item
`version_option_show_python` at version 4 `approved`, its ticket, the three
criteria, bg_4 `pending`, the statement s3, bg_1 and bg_3 merged with
their `delivered:` rows, and the ledger row `l_d24f6997d1` of m399. The
door stamps the item and the criteria into the page's refs. The call
`rulings.rule(rulings={"1": "revise", "2": "approve", "3": "approve", "4":
"approve", "5": "contest"}, words=<m400's words>)` is admitted. After
`apply_rulings`, the item is `contested` at version 4, `verdict:<id>`
names it `revise`, and `_resolve_contest` returns `principal_said` equal
to m400's words. The call `{"5": "revise", ...}` is refused with line 1
named. A second case, s172's turn: the relay of `{confirm_with_default_on_eof:
revise}` refuses `problem.set_approval(id="confirm_with_default_on_eof",
approval="approved")`.

### 2.3 The Architect's reply: no new row about a row the principal ruled

**The mechanism.** A seat that the principal's ruling reaches does not
answer it with a new ledger row about the row that was ruled. The door
holds this, and the brief stops asking for the row.

1. `ledger.log` (`api.py:7102-7173`) refuses, in a session whose trigger
   is a relay caused by a principal `verdict`, a row whose `about_ref` is a
   ref of that relay: "the principal ruled on <ref> in the relay that woke
   you, and their words are on file as their decision. A new assumption
   about the same row goes back on their page as your reading of their
   words. Adopt what they approved, and stop." The check is mechanical:
   `ctx.trigger`'s verb is `relay`, its cause's sender is `principal` and
   its verb is `verdict`, and `about_ref` is in the trigger's `body_refs`.
   It holds for the Architect, the Terminologist and the Vision Keeper
   alike, the three writers of the 117 reply rows.
2. `ledger.log` refuses an assumption of fewer than four words: "an
   assumption is a sentence a reader learns from. Name what went unread,
   why, and what a reader would get wrong." This is the blindspot brief's
   own rule, "Say the actual thing", held at the door. s87's 56 calls with
   one word each would read it.
3. `model.adopt` and `glossary.adopt` read a string `ids` as a list of one
   id. s559's call then reads `parametersource_commandline` whole, and
   `_adopt_rows` skips it, because the ruling did not approve it.
4. `architect/relay.md` changes its contested paragraph to:

   ```
   A **contested** row is not yours to fix in this session. It stays observed,
   on file as contested, and the principal's words are on file as their
   decision. Do not log an assumption about it: the door refuses a row about a
   row the principal just ruled. When the words ask for something to be built,
   that is the request's, and the request is on the principal's page. With no
   approved id, end the session with no call.
   ```

   The step "End the session with no call." moved 0 of 5 replies on
   night 126, and a named one-line reply moved 5 of 5 (copied:
   `plans/operating-facts.md`, frame 165). The door of point 1 holds the
   behaviour, so the brief's sentence is a cue and not the guard.

**What closes the loop of s557 to s560.** In s557 the reply names line 1,
the item, because 2.1 put it there, and point 1 of 2.2 refuses a revise on
the note. The ruling on the item wakes the Vision Keeper and not the
Architect. If the Liaison contests the note too, s559's relay still runs,
by the ruling of 2026-09-03, but its `ledger.log` is refused and its
`model.adopt` skips. No open row is left, so `tick_agenda` returns nothing
and s560 does not run. `annotate` runs for bg_4 on the next pass.

**What the frames get.** Covers night 136's wall 3, the new row that is
the next page. Covers frame 45's writer for the one-word rows that night
136 shows. Frame 45's own shape, a row that names a verdict no row holds,
has no case on nights 133 and 136, so frame 45 keeps its place for that
shape. Covers the source of frame 184's two words.

**The test.** Night 136, s559's turn. Rebuild inline the relay m422 with
`principal_verdict` and `principal_said` as s559's prompt holds them, its
cause the verdict m421, and the constraint `parametersource_commandline`.
`ledger.log(about_ref="parametersource_commandline",
about_table="constraints", assumption=<s559's words>)` is refused with
the sentence of point 1. `model.adopt(ids="parametersource_commandline")`
returns the id skipped. A second case, s87's turn of night 136:
`ledger.log(about_ref="@term:time", about_table="model_areas",
assumption="term")` is refused with the sentence of point 2.

### 2.4 The next page: a reply row is not a page, and the agenda waits for the start work

**The mechanism.** Two edits.

1. **The agenda skips a reply row, and reads the request's lineage
   first.** `tick_agenda` (`scheduler.py:931-972`) counts and picks open
   ledger rows less the reply rows. A reply row is the join of 1.4: its
   writer session, from `receipts` with `table_name = 'ledger'`, was woken
   by a relay whose cause is a principal `verdict`, and the row's
   `about_ref` is in that relay's refs. 2.3's door stops these rows at
   write time, and the predicate holds the same rule for a row that
   reaches the ledger by another writer (`_stage_ledger` has five
   callers, `rota.tools.map table ledger`). A reply row stays `open` and
   countable. It rides the next page that the agenda sends for another
   row, as a team's note. While an open request exists, the agenda picks
   rows whose `about_ref` reaches that request first (its item, ticket,
   criteria, tests, statement or batch), then the others by `rowid`. Law 8
   presents a lineage's assumptions at its gates, so the request's own
   lineage comes first.
2. **`agenda` moves to band `start`.** In `predicates.py:1571` the band
   changes from `gate` to `start`. The predicate stays where it is in the
   file, after `observed_entries`, `annotate`, `touch_note`, `batch_start`
   and `tests_missing`, so each of those runs first. The ruling of
   2026-09-13, point 2, says "After that, nothing waits on a page", and
   point 4 makes band order the lever. The tipsV reason for band `gate`
   is held by the onboarding gate, which stays. Two effects follow, and
   the night read checks both: at the end of onboarding the
   `observed_entries` page comes before the first agenda page, and
   `signoff` and `awaiting_confirm`, band `gate`, come before every agenda
   page.

**What the predicate reads to skip a row.** `ledger`, `receipts`,
`sessions.trigger_msg`, and `messages` for the trigger and its cause, one
join per open row. Night 133's s228 woke with 30 open rows (observed: its
`wake_detail`, `ledger=30`), so the join is cheap.

**What the frames get.** Covers night 136's wall 5, `annotate` starved by
`agenda`. Covers the "next page" half of wall 3. Leaves frame 41's wall,
a page open at a walk's end, in its place.

**The test.** Night 136, the state after s567. Rebuild inline bg_4
`pending` with no `batch_touch` row, its item `approved`, and the open
ledger row `l_62ca6652d9` with its receipt to s567, whose trigger is the
relay m430 caused by the principal verdict m429, naming
`parametersource_commandline` (observed: `sessions`, `messages` and
`receipts`, night 136, 2026-10-09). `tick_agenda` returns no wake.
`scheduler.frontier` (`scheduler.py:1177`) offers `tick:annotate` on bg_4. With a second open
row from `reconcile`, the agenda wakes with that row alone.

### 2.5 The touch note names a criterion with no test

**The mechanism.** The touch note and the quarantined page carry the
item's criteria (2.1), and each criterion's `check:` line says whether a
test exists.

1. On the touch note, before the build, each criterion reads `check: none
   yet.`, because the Tester writes no test before the head commit.
2. When a `tests_missing` key of the batch is quarantined, a criterion
   with no test reads `check: none. The team gave up writing it after
   <n> tries.` The count comes from `tick_attempts`, as `render_state`'s
   `gave_up_on` reads it (`principal.py:244-247`).
3. A predicted path under `tests/` that the code index does not hold reads
   `(a new file)` on the team's prediction line. `touch_words`
   (`principal.py:761-782`) reads `code_index` for the path.
4. The quarantined page keeps `quarantined.md`. The door stamps the item
   and the criteria (2.1), so a quarantined batch renders as the request
   block, then the team's prediction, then one line read from the keys:
   "The team gave up on: tests_missing for bg_2, 3 attempts."

**What the frames get.** Covers frame 189's page half, "the page says when
a criterion's test file does not exist", and night 136's wall 6. Leaves
frame 182, a criterion merged with no test of its own, in its place.

**The test.** Night 136, s184's dispatch and s185's turn on m85. Rebuild
inline bg_2 `pending` with no head commit, its item, the three criteria,
no test row, and the three `batch_touch` rows. The page numbers the item
as line 1, the three criteria as lines 2 to 4 with `check: none yet.`,
and the prediction as line 5 under "The team expects to touch:". The call
`rulings.rule(rulings={"1": "approve", "2": "approve", "3": "approve",
"4": "approve", "5": "contest"}, words=<m85's words>)` is admitted. After
`apply_rulings`, the verdict holds `bg_2: contest`, the relay split sends
bg_2 to the Architect, and `_mode_key` gives `annotate`. A second case,
s200's dispatch: with `tester|tick:tests_missing|bg_2` quarantined at 3
attempts and tests for cr_1 and cr_2 only, the page reads `check: none.
The team gave up writing it after 3 tries.` under cr_3.

### 2.6 The frames, in one table

| Frame | Change | Covered | Left open |
|---|---|---|---|
| 45, an abandoned tick on the page as a finding | 2.1, 2.3 | the one-word blindspot rows of nights 133 and 136 | a row that names a verdict no row holds. No case since night 86 |
| 184, the ask-back from `recent_chat` | 2.1, 2.3 | the two words' source | the copy of the seat's own ask. Night 136 had 0 such ask-backs after frame 142's answered-question door (copied: `plans/night136-read.md`, section 1) |
| 185, `a separate request, for later` | none | none | all |
| 186, the grouping on a contested item | none | none | all |
| 187, the contested tick re-wakes the Vision Keeper | none | none | all |
| 188, the Liaison's self-relay | 2.3 | no new reply row to relay back | the mode for a self-relay |
| 189, the prediction page | 2.2, 2.5 | both halves of its mechanism | its ratio, read on the night |

## 3. The tests and the cassettes

Each test rebuilds its rows inline, as `tests/rota/test_desk_guards.py`
does with `_night_rows`. The night databases are ignored by git.

| Change | Case | Real turn | Rows | Kind |
|---|---|---|---|---|
| 2.1 | the agenda page numbers the open request and its criteria first, and the seven rows after the heading | night 133, s228's dispatch and s229's turn on m122 | inline | door, `request_rows`, `render_page`, `rulings.rule` |
| 2.1 | the park page renders word for word as before | night 132, m117, frame 142's case | the existing case | `render_page` |
| 2.2 | a revise of line 1 lands on the item with the words, and a revise of the note is refused with line 1 named | night 136, s537 on m400, and s557 on m420 | inline | sandbox, `apply_rulings`, `_resolve_contest` |
| 2.2 | the Vision Keeper's relay cannot set a revised item approved | night 136, s172 on m76 | inline | sandbox |
| 2.2 | an approve of an item line on an agenda page leaves a contested item contested | night 136, m362's rows with the item contested | inline | `apply_rulings` |
| 2.3 | a relay of a ruling cannot log a row about the ruled row, and `model.adopt` reads one id | night 136, s559 on m422 | inline | sandbox |
| 2.3 | a one-word assumption is refused | night 136, s87's call on `@term:time` | inline | sandbox |
| 2.4 | the agenda skips a reply row, and `annotate` runs before the agenda | night 136, after s567 | inline | predicate, frontier |
| 2.5 | the touch note numbers the criteria with `check: none yet.`, and a contest of the prediction reaches the Architect's `annotate` | night 136, s184's dispatch and s185 on m85 | inline | door, `render_page`, sandbox, `_mode_key` |
| 2.5 | the quarantined page says the team gave up on cr_3's test | night 136, s200's dispatch, m96 | inline | door, `render_page` |
| 2.2 | the Architect re-annotates from the principal's words | night 136, a relay of `{bg_2: contest}` with m85's words | inline | sandbox, `batches.annotate` |

**Recorded cases whose prompts change** (reasoned: the `prompt:` and
`tick:` keys of `tests/rota/cases/*.yaml`, read by grep, 2026-10-09). The
gate prints the stale set on its five lines. `python -m rota.tools.gate`
re-records the stale cases unless `--no-rerecord` is passed, and
`--rerecord-now` re-records while the main card is held (observed:
`python -m rota.tools.gate --help`, 2026-10-09). This agent did not run
the gate.

- The 7 `l1_landing.yaml` cases: the `landing` working set holds the page
  text (`runner.py:1604-1611`), and the page gains the request block and
  the team's heading. Re-record.
- `L1-AR-adopt-what-the-principal-approved` (`l1_unresolved.yaml:256`):
  `architect/relay.md` changes. Re-record.
- `L1-AR-annotate-a-batch` (`l1_architect.yaml:13`): `annotate.md` gains a
  paragraph. Re-record.
- `L1-LI-relay-a-ruling-without-interpreting-it`,
  `L1-LI-a-ruling-splits-by-owner` and
  `L1-LI-a-park-verdict-sends-its-contested-criterion-to-the-terminologist`
  (`l1_liaison2.yaml:68`, `:316`, `:540`): `verdict_signoff.md` changes.
  Re-record.
- `L1-LI-say-what-the-run-could-not-see` (`l1_survey.yaml:195`): the
  one-word door can refuse a recorded call, which moves the next turn. Its
  expectation, one `survey_records` write, holds. The gate's stale line
  decides.
- `L1-TE-adopt-what-the-principal-approved` (`l1_unresolved.yaml:223`):
  the reply-row door can refuse a recorded `ledger.log`. The gate decides.
- No change expected: `L1-LI-put-the-open-assumptions-to-a-present-principal`,
  `L1-LI-present-the-touch` and `L1-LI-surface-a-quarantined-message`. Their
  briefs and working sets do not change, and their expectations read
  `refs_include`, which the stamped refs keep. The two
  `L1-VK-amend-a-contested-item` cases change only if a fixture rules
  `revise`.
- Two new cases, recorded at 5 runs each.
  `L1-AR-a-ruled-constraint-gets-no-new-row` replays s559's relay and
  expects no `ledger` write and no message.
  `L1-AR-re-annotate-from-the-principals-correction` is a relay of `{bg_2:
  contest}` with m85's words in mode `annotate`, and expects one
  `batch_touch` write naming `tests/test_termui.py`.

**Unit tests that assert the old words.** The implementer rewrites each to
the new page and keeps its intent. `tests/rota/test_park_page.py:597`
asserts the batch-line refusal for every batch. The page words stand in
`tests/rota/test_principal_messaging.py` and
`tests/rota/test_signoff_assumptions.py`. The implementer runs
`python -m rota.tools.map fn render_page` and greps the tests for "Where
you did not say" and "Before I build this" first.

## 4. What the design does not change, and why

- The park page and the note of frame 142 stay as they landed. 2.1 moves
  their request block into a shared helper, and the words do not change.
- A contest of a team's note still relays its `about_ref` to the desk that
  assumed it (ruled: 2026-09-03, "contest with words goes back to the desk
  that assumed it"). 2.3 changes what the desk does with the relay, and not
  the route.
- The ledger stays the record of assumptions, and the agenda stays the page
  that presents them (law 8). 2.4 changes which rows come first and which
  rows wake it.
- `PAGE_ASSUMPTIONS`, seven, stays. The request block does not count
  against it, because its rows are not open assumptions.
- `quarantine_looping` and `loop_cap` stay the bound on a loop through the
  principal, as frame 142 left them.
- The agent principal and `probes/principal_brief.md` stay. The page text
  changes, and the agent reads the page. Meta workflow.
- `rulings.rule`'s three words stay. Frame 185's fourth word, a put-off
  request, is its own frame.
- The cancel on an amended item stays (ruled: 2026-09-12, point 3, level 2).
  Whether the ticket and the criteria are sliced again is open question
  5.1.
- The touch note stays a sense check with no gate (R7, 2026-09-03). A
  correction of the prediction reaches the Architect and does not stop the
  batch.

## 5. The open questions

Each was checked against the records first: `rota/LAWS.md`,
`rota/DECISIONS.md`, frame 142's design and the briefs. The records answer
four questions that the design met, and those are not asked:

- Whether a page of seat rows goes to the principal: yes, with the request
  first. Law 8 and the ruling of 2026-09-03 put a lineage's assumptions to
  the principal, and only a decision closes a ledger row (law 11's note).
- Whether the agenda may wait behind the start work: yes. The ruling of
  2026-09-13, point 2, says "nothing waits on a page" after the first page,
  and point 4 makes band order the lever.
- Whether a contest of a note still reaches its desk: yes, by the ruling
  of 2026-09-03.
- Whether an approve on an agenda page may change an item's approval: no.
  Law 8 gives the item's approval to the sign-off gate, and law 9 stamps it
  against the version the principal saw there.

Two questions stay open:

1. **[high] When the principal's words amend an item before it is
   delivered, are its ticket and criteria sliced again?** The records: the
   ruling of 2026-09-12, point 3, says an amended item "cancels a running
   batch built from it and re-batches". `tick_slicing` slices again only an
   item delivered at an older version (`scheduler.py:264-287`). So after
   2.2 the item holds the principal's line, and the new batch builds from
   the old criteria. Night 133's walls 4 and 5 sit beside this, frame 129.
   Recommended: yes, as its own frame below frame 190, ordered next after
   it. The cost is on the slicing path, which no change here touches, and
   2.2 is still worth its price without it, because the line reaches the
   item and the sign-off page.
2. **[med] Does the Tester's wake show the batch's expected test paths?**
   The records: `tester/tests_missing.md` says the Tester chooses the path,
   "Nobody assigns them". On night 136 the tests of bg_2 and bg_3 went to
   `tests/test_utils/`, and the touch set and the principal named other
   files. After 2.2 the Architect's corrected prediction names the file the
   principal wanted, and the Tester does not read it. Recommended: yes. The
   `tests_missing` working set gains the batch's expected paths under
   `tests/`, and the brief gains one sentence: "A path under `touch` is the
   file the principal expects your tests in. Use it." This goes in pass 2,
   about 20k more, with one re-record of the `tests_missing` cases.

## 6. Price

The prices come from `plans/operating-facts.md`, "Cost anchors": a cold
implementer pass of 18 files, 666 insertions and 11 tests cost 216.9k on
the harness line (frame 66), and a reviewer pass on eight points cost
146.7k (frame 66). Frame 142's two passes were priced at 200k and 80k, with
reviews of 120k and 80k. A cap in a brief does not bind. Meta workflow.

- **A design review on Opus**, on this record before any code: about 125k,
  the stack's line.
- **Pass 1, the page: 2.1 and 2.5.** Files: `rota/roles/principal.py`
  (`request_rows`, `request_block`, `render_page`, `_park_page`,
  `touch_words`), `rota/core/sandbox.py` (the present door's stamp), and
  the tests of 2.1 and 2.5 with the rewrites of section 3. About 250k for
  the implementer and about 130k for its diff review. It lands first,
  because 2.2's door reads the item line that 2.1 stamps.
- **Pass 2, the route and the reply: 2.2 and 2.3.** Files:
  `rota/roles/api.py` (`rulings_rule`, `ledger_log`, `model_adopt`,
  `glossary_adopt`, `problem_set_approval`, `batches_annotate`),
  `rota/roles/principal.py` (`land`), `rota/core/runner.py`
  (`_resolve_contest`, `_mode_key`), `rota/core/sandbox.py`
  (`_owner_of_ref`, the relay split), `rota/core/scheduler.py`
  (`park_criterion_relay`), the briefs `architect/relay.md`,
  `architect/annotate.md` and `liaison/verdict_signoff.md`, and the two new
  cases. About 280k for the implementer and about 140k for its diff
  review. Re-records, GPU apart: the 7 landing cases, the 3
  `verdict_signoff` cases, 2 Architect cases, and the 2 new cases at 5
  runs.
- **Pass 3, the next page: 2.4.** Files: `rota/core/scheduler.py`
  (`tick_agenda`), `rota/core/predicates.py` (`agenda`'s band), and the
  test of 2.4. About 100k for the implementer, on the anchor of 77k for one
  tool with 20 tests and a gate run (frame 24), and about 80k for its diff
  review.
- **One night after the three passes**, as the walk, to read the three
  ratios of the ends-when and the two effects of 2.4's band move.

Total in agents: about 1.1M, three implementer passes and four reviews.
Recommended: three passes, one implementer resumed by message for each,
because the passes share `principal.py` and `sandbox.py` and the resume
carries the delta.
