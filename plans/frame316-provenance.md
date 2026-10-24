# Frame 316, the provenance read: an agenda page carries other items' rows

Rota workflow. Read on 2026-10-24 by one agent on Opus, read-only, at
fe4b3c78. The `rota/` tree at fe4b3c78 and at the branch head 50609cd3 is
the same (observed: `git diff --quiet fe4b3c78 HEAD -- rota/`), so every
line number below holds at both. The database is
`.rota/clickI_night161.db`, opened `?mode=ro`. The function results on its
end state come from calls of the real functions on that database.

## Result first

The wall has two causes, one a design choice and one a bug.

1. **A design choice that frame 241 already names.** `off_page` keeps on a
   later request's page every ledger note about a delivered item of an
   earlier request, "so a ruling closes it" (observed:
   `rota/roles/principal.py:944-985`, the exception at line 982). Frame
   193's design, 2.F.7, chose this on 2026-10-10 to answer review finding
   4. Frame 198 and frame 204's design, section 5, replaced it with a park
   at the merge, but frame 204 is parked and the park was never built
   (observed: no `ledger SET status = 'parked'` in `rota/`).
2. **A bug in frame 274's fix.** In `land`, the skip that stops a note's
   contest from contesting another request's item calls
   `request_of(conn, row["about_ref"])` (observed:
   `principal.py:2205-2208`). `request_of` reads only an item id
   (`principal.py:818-831`). For a note whose `about_ref` is a criterion, a
   ticket or a test, it returns None, and `owner is None` lets the carrier
   contest that row. So "take them off this page" contested `cr_1`, and
   s409 respecified the merged confirm item's `cr_1`.

The ticket names `tk_2` and `tk_2_version_option_show_python` join no rows
in any query (observed). The collision is a naming rule of
`tickets_slice` and has no part in the wall.

## The chain, night 161, walk 3

1. The b_3 merge delivered `confirm_default_on_eof` at 04:19, and b_1
   delivered `echo_json` earlier. Their open ledger notes stayed open
   (observed: `config` `delivered:echo_json` 1, `delivered:confirm_default_on_eof` 4).
2. `tick_agenda` woke the Liaison five times with the oldest seven open
   rows of the whole night: s350 `ledger=27`, s355 `ledger=20`, s391
   `ledger=18`, s398 `ledger=12`, s406 `ledger=5` (observed:
   `sessions.wake_detail`, `wake_refs`).
3. Each page's request was e_p3, `version_option_show_python`, and
   `off_page` dropped nothing (observed: `page_request` gives `e_p3` and
   `off_page` gives `set()` for the refs of m191, m218, m225 and m233).
   The rows of other items per page, of 7 note lines: m191 4 (echo_json),
   m218 2 (confirm), m225 6 (confirm), m233 5 (confirm, with one note about
   `tst_4_confirm_default_on_eof` that reaches no item) (observed:
   `ledger.about_ref` of each ref). The page did not grow in lines. The
   share of confirm notes grew as the version notes drained (reasoned:
   `tick_agenda` sorts the request's own rows first,
   `scheduler.py:1093-1110`).
4. The page names no item on a note line. It says "They are not your
   request" above them (observed: `clickI.principal.jsonl`, night 161,
   m225 and m233). He read them as the confirm or echo change from the
   text, and was right each time.
5. Each "take them off this page" became `contest` on those lines (observed:
   `rulings.per_item` of r_e1e0b9a1d8, r_40c94b2c6d, r_288739e866,
   r_810ee68dc8). `land` closed each note as overruled
   (`principal.py:2209-2214`), and the carrier put each note's `about_ref`
   into the verdict refs (step 6). The notes did close. The 27-row ledger
   drained to 0 through 4 of his asks.
6. The verdicts and relays went to the delivered items' owners (observed):

| Ask, reply, seat | Verdict refs of another item | Relays | What the seat did |
|---|---|---|---|
| m191, m192 and m194, Liaison s356, s357 | m195: `c_2`, `r_a1ca6cbbe0` (echo_json) | m196 to the Architect, `r_a1ca6cbbe0` | no row change found |
| m218, m219, s392 then s393 | m220: `cr_1_confirm_default_on_eof`, `tk_1_confirm_default_on_eof` | m221 Architect, m222 Terminologist | no respecify of a confirm row |
| m225, m226, s399 then s400 | m227: `tk_2`, `cr_1/2/3_confirm_default_on_eof` | m228 Architect `tk_2`, m229 Terminologist | no respecify of a confirm row |
| m233, m234, s407 then s408 | m235: `cr_1`, `tst_4_confirm_default_on_eof` | m236 Terminologist `c_6_...`, `cr_1` | s409 respecified `cr_1` five times and answered the Tester |

   Six relays reached the owners of two delivered items. One wrote. s409
   read m234's words, which also fault line 7, the b_5 check, and applied
   them to both refs of its wake (observed: s409's calls; reasoned: the
   wake held `cr_1` beside `c_6`).

## The answers

**1. The page builder and its query.** Three functions build the agenda
page (observed):

- `tick_agenda`, `rota/core/scheduler.py:1036-1127`, selects
  `SELECT id, about_ref FROM ledger WHERE status = 'open' ORDER BY rowid`
  at line 1067. The query has no item and no request filter. Only held
  items leave (`held_items`, lines 1080-1089), and a delivered item is not
  held. The rows that reach an open request sort first (lines 1095-1110).
  The wake carries the first `PAGE_ASSUMPTIONS` = 7 (`sandbox.py:34`).
- `off_page`, `rota/roles/principal.py:944-985`, removes refs from the
  send door (`sandbox.py:3746`) and from `request_rows` and `render_page`
  (`principal.py:1005`, `1580`). Line 982 keeps a ledger note whose items
  are all delivered.
- `request_rows`, `principal.py:988-`, adds the request's item and
  criteria, which is why the page also holds `version_option_show_python`
  and `c_2` to `c_6`.

Rows of another item reach the page because the page is scoped to one
request, not one item, and the 2.F.7 exception keeps a delivered earlier
request's notes in that scope on purpose (observed: the docstring at
`principal.py:945-951`).

**2. The ticket names.** `tickets_slice`, `rota/roles/api.py:4637-`, gives
the first slicer the bare id and a later item the id with its item name
appended, line 4692, "two items never share a ticket id" (observed). s191
sliced bare `tk_2` for confirm first, and s281 then got
`tk_2_version_option_show_python` (observed: `tool_calls`). Every lookup
is by exact id: `_items_reached('tk_2')` gives `confirm_default_on_eof`,
and the version ticket gives its own item (observed). So no query joins
the two items' rows, in `tick_agenda`, `off_page` or `land`. The page
prints no ticket id (observed: the page text). The bare name can mislead
a model that reads `tk_2` in a relay (m228), but no seat acted on that
(reasoned: no Architect write follows m228).

**3. The route of "take them off this page".** The table in the chain
gives each seat and verdict. The Liaison has no verb for "off this page".
It reads the words as `contest` on the named lines, which is the only
ruling that does not approve (reasoned: `rulings.rule` takes approve,
contest and revise). The contest lands in `land`, `principal.py:1921-`:
the note closes, a principal decision is written with `refs` =
`[about_ref]`, and the carrier at lines 2194-2208 adds `about_ref` to
`per_item` unless the note's owner request differs from the page's. The
check at line 2205 gives None for `cr_1`, `tk_2`, `cr_*_confirm_*`,
`tk_1_confirm_*`, `c_2` and `tst_4_confirm_*`, so it never fires on these
rows (observed: `request_of` on each id). The verdict refs are the
`per_item` keys that are not closed, line 2252. The Liaison relays each to
its owner. s409 respecified `cr_1` because its wake m236 named `cr_1`, and
m234's words fault "line 7's check", which s409 had no page to place
(reasoned).

**4. The design history** (observed: `git log -S`, the archived stacks,
the design pages).

- `tick_agenda` dates from b519a246 (2026-08-10). Frame 190's design
  (2026-10-09, 0ffc97b7) added the request sort, "The request's own lineage
  first, by law 8".
- Frame 193's design 2.3 first ruled "One request per page" and dropped
  "all delivered items of an earlier request" (`plans/frame193-design.md:418-440`).
  Its 2.F.7 then reversed the drop: "That rule goes. Such a row, night
  137's six `echo_json` rows, renders under the team's notes as any note
  does, and a ruling closes it (2.F.9, finding 4)" (lines 830-834).
  Built in 61a0f41d (2026-10-10), and pinned by
  `tests/rota/test_frame193_pass2.py:335-337`, "A note about the delivered
  echo_json item stays a line, so a ruling closes it".
- Frame 198 (archive `stack-2026-10-14.md:148`) named the residue on night
  139, and `plans/frame198-scope.md:59` recommended "a park and not a
  close": "The park takes the rows off the agenda wake and off every later
  page". Frame 204's design, section 5, adopted it as frame 198's option
  (a), with Roman's "they can reach me if they are shown quietly" (ruled:
  Roman, 2026-10-11 15:00). Frame 204 is parked, and its pass 3, the page
  and the park, has no commit (observed: the stack heading, no `parked`
  ledger status in the code).
- Frame 241 (open, `plans/stack.md:1690`) holds the same site. Its status
  of 2026-10-17 04:31 names this cause: "`off_page`'s rule that a note
  about a delivered item of an earlier request stays so a ruling closes
  it". Nights 149 to 153 each show it.
- Frame 274 (archive `stack-2026-10-18.md:88`, db1296e1, 2026-10-16) added
  the carrier skip. Its count read only notes whose `about_ref` "is in
  `items`" (`plans/frame274-count.md:66-77`). The criterion, ticket and
  test cases were outside the count, so the gap at line 2205 was never
  measured.

So the page was scoped to one request from frame 193, never to one item.
The delivered-note exception was a deliberate choice, and its replacement,
the park at the merge, was designed and not built. Frame 274's guard has a
real bug. Neither is drift.

## The repair, named

1. **`land`, `principal.py:2205-2207`**: read the owner from the items the
   note reaches, `request_of` over `_items_reached(conn, row["about_ref"])`,
   and skip when every reached item belongs to another request. A note
   that reaches no item keeps today's carrier. 1 cycle: one predicate, its
   tests, one review (reasoned).
2. **The park at the merge, frame 204's pass 3 as frame 198's option (a)**:
   at a batch's merge, park every open ledger row whose items are all that
   batch's delivered item. `tick_agenda`'s query then skips them, and
   `render_state` lists them under the merged request. Remove the 2.F.7
   exception at `principal.py:982` only if the park makes it dead, and
   move the pin at `test_frame193_pass2.py:335-337` with it. 2 cycles
   (reasoned: the design exists; one schema status, one merge hook, one
   tick filter, one state view list, one review).
3. **Out of scope here, named.** A note about a test reaches no item,
   because `_items_reached` has no `tests` lookup, so `off_page` keeps
   l_8fd20d7618 on any page (observed: `tst_4_confirm_default_on_eof`
   gives `[]`). This is frame 209's review finding 1, and frame 204's
   pass 3 owns it.

Price: 3 cycles in all. Repair 1 alone stops the wrong respecify. Repair 2
stops the pages. Frame 316 and frame 241 hold the same cause, so one frame
can take both (reasoned).

## The red tests

Build each from night 161's rows at the stated session.

1. `land` on r_810ee68dc8 (ask m233, reply m234, the per_item in the
   record): the verdict refs hold `c_6_version_option_show_python_help`
   and hold neither `cr_1` nor `tst_4_confirm_default_on_eof`. No relay to
   the Terminologist names `cr_1`.
2. `land` on r_288739e866 (m225, m226): the verdict refs hold no `tk_2` and
   no `cr_1/2/3_confirm_default_on_eof`.
3. `land` on r_40c94b2c6d (m218, m219): the verdict refs hold no
   `cr_1_confirm_default_on_eof` and no `tk_1_confirm_default_on_eof`.
4. `land` on r_e1e0b9a1d8 (m191, m194): the verdict refs hold no `c_2`.
   `r_a1ca6cbbe0` reaches no item, so it stays (reasoned: the carrier is
   kept for a note of no request).
5. `tick_agenda` after the b_3 merge, at s391's state: the wake refs hold
   no `l_2d8cfe55d7` and no `l_843f17e810`. At s398's state the wake holds
   none of the six confirm rows. At s406's state the four `cr_1` rows wake
   no page.
6. `tick_agenda` after the b_1 merge, at s355's state: the wake refs hold
   no `l_511c47ccd1`, `l_ed04dbc3f3` or `l_01d2b707a4`.

Tests 1 to 4 are red today and go green on repair 1. Tests 5 and 6 are red
today and go green on repair 2. The pin at
`test_frame193_pass2.py:335-337` changes with repair 2 only.
