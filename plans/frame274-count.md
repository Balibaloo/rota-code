# Frame 274, the keypress's inferred carrier: the count and the design

Reader: one Opus agent, read-only, 2026-10-16. Meta workflow for this
record. Rota workflow for every fact in it. Script:
`scratchpad/f274/count.py` of session 04be1489, output `count_out.txt`
beside it. Every database opened `mode=ro`.

## 1. The code

The carrier is in `land`, `rota/roles/principal.py` 1763 to 2081. The rows
it reads, in order:

1. `per_item = dict(answer.per_item or {})` and
   `ruled = set(answer.per_item or {})`, lines 1849 and 1851. `ruled` is the
   ruling as given, before any filter.
2. `stamped = set(door_rows(conn, ask.message_id, "stamped"))`, line 1892.
   This reads `config` key `stamped:<ask id>` (`door_rows`, 1735 to 1744).
3. For each ledger ref ruled approve, contest or revise: the open `ledger`
   row (`id, about_ref, default_taken, kind`), then `item_provenance` of
   `about_ref`.
4. The inference, lines 1971 to 1974:

```python
            if row["about_ref"] not in ruled and \
                    not (about and about["provenance"] == "observed") and \
                    row["about_ref"] not in stamped:
                per_item[row["about_ref"]] = "contest"
```

5. A `decisions` row `overruled at signoff: <words>` resolves the ledger
   row, and the ledger row goes to `resolved`.
6. The per-item loop writes `items`, lines 2004 to 2006:
   `UPDATE items SET approval = ?, approval_ver = version WHERE id = ? AND approval IS NOT ?`.
   It then lifts quarantines on a change.

The carrier never reads the page's request. The page's request is known
in the same function only as `ask.refs`, the page's `messages.body_refs`.
The function `page_request(conn, refs)` (915 to 935) gives the request
entry that a page's refs reach. The function `request_of(conn, item)`
(812 to 825) gives an item's request entry. `land` calls neither. The
carrier also never asks whether `about_ref` is delivered or merged.

Callers of `land`, all through one path:

- `pump` (`principal.py` 1728), called by `rota/core/loop.py` 232 (the
  agent principal of a night) and `rota/cli.py` 845 (`OneShot`, the real
  principal's one-shot answer).
- `apply_rulings` (`principal.py` 2186), called by `rota/core/runner.py`
  5033 after a session commits a `rulings` row. The Liaison's reading of
  his words lands here. Night 152's r_e3e9d2c047 landed by this caller.

So the agent principal and the real principal share the carrier
(observed: the call sites above, 2026-10-16). `rota/testkit/scenes.py`
1559 calls a different `land`.

## 2. The count, nights 130 to 152

Databases: `.rota/clickI_night<N>.db`, N = 130 to 133 and 135 to 152.
Night 134 has no copy. Table reads: `rulings` (landed), `ledger`,
`decisions`, `item_provenance`, `config stamped:*`, `messages.body_refs`,
`items`, `batches`.

- Contests or revises of a ledger note in a landed ruling: 732.
- Of those, the current guards stop 240: 160 `ruled`, 80 `observed`.
  None hit `stamped`.
- The carrier writes an item on 42. That is, the note's `about_ref` is in
  `items`, the ledger row was open (a principal `overruled` decision
  resolves it), and no guard stops it. One more row, night 133 m229
  `l_5040671af5`, has no `overruled` decision, so the ledger row was not
  open and the carrier did not fire.

`about_ref` is in the page's `body_refs` on 0 of the 42 (observed). The
reason: a page item in `body_refs` is in the ruling, so `ruled` stops it.

**The sign, an item of another request contested through a note: 6 of
42 carrier fires, in 5 rulings.** "Another request" means
`request_of(about_ref)` differs from `page_request(ask.refs)`.

| Night | Ruling | Page, reply, verdict | Note | Item set contested | Item's request, page's request | Item's state |
|---|---|---|---|---|---|---|
| 133 | r_6cbce9f3d1 | m377, m378, m379 | l_5922514ada | echo_json | e_p1, e_p3 | bg_1 merged |
| 133 | r_6cbce9f3d1 | m377, m378, m379 | l_b2d0199f1b | confirm_default_on_eof | e_p2, e_p3 | other request, batches abandoned |
| 133 | r_acb0a379d3 | m396, m397, m398 | l_5922514ada | echo_json | e_p1, e_p2 | bg_1 merged |
| 133 | r_7e3061925f | m415, m416, m417 | l_b2d0199f1b | confirm_default_on_eof | e_p2, e_p3 | other request |
| 151 | r_9518c2a452 | m83, m84, m85 | l_cb9936ee70 | echo_json | e_p1, e_p2 | other request, bg_2 merged |
| 152 | r_e3e9d2c047 | m59, m60, m61 | l_a5ef6d4cd8 | echo_json | e_p1, e_p2 | bg_1 merged before m59 |

All 6 are wrong by his words. m378: "the JSON echo helper and the confirm
flag are separate requests for later, and none of the three is
contested". m397 and m416 say the same. m84: "Line 6 belongs to my first
change, the JSON echo helper, so please take it off this page". m60:
"echo_json is my first change, not this one". Merged at the ruling: 4 of
6 echo_json writes by `batches` (final state, so the time is reasoned for
nights 133 and 151; night 152's merge before m59 is observed by the cycle
read). Another request, not merged: 2 of 6, both `confirm_default_on_eof`
on night 133.

**Night 151 has the same writer.** Verdict m85 (seq 87) already carries
`echo_json` in `body_refs`. The relay m87 (seq 89) carries it to the
Vision Keeper. Session s200 woke on m87 and then sent
`problem.set_approval(approval='contested', id='echo_json')` at seq 2
(observed: night 151 `messages` and `tool_calls`, 2026-10-16). So the
carrier set `echo_json` contested first, and s200 repeated a same-value
write that the relay invited. Frame 268's site, the Vision Keeper's
`set_approval` on a relay, is likely not the cause of its own night 151
case (reasoned: the order of the rows). Frame 268 should be read against
this before its pass.

**Right cases, which a fix must keep: 36 of 42.** The proposed predicate
refuses 0 of 36.

- Account and onboarding pages, no request on the page
  (`page_request` is None), notes about descriptions such as
  `defines_commands_and_options`, `how_it_works`, `executes_commands`:
  nights 133 (m35, m39), 135 (m10 twice, m127), 139 (m30), 140 (m30, m36
  twice, m55), 142 (m18 twice), 143 (11), 144 (10). Total 33.
- A note about the page's own request item: night 136 r_f98fa213d9, m165,
  `l_fbbef84c1e` about `confirm_with_default_on_eof` (e_p2 = page e_p2).
  His words: "line six ... leaves out that the new flag is off by
  default". This is the cleanest right call. Night 133 r_7e3061925f,
  `l_f12f8f781d` about `version_option_show_python` (e_p3 = page e_p3).
  Night 133 r_acb0a379d3, `l_b2d0199f1b` about `confirm_default_on_eof`
  (e_p2 = page e_p2). Total 3.

Residue that the predicate keeps and his words do not support. These are
other causes, not this frame's:

- Night 133 m396, `confirm_default_on_eof`: the page has only notes, so
  `page_request` reads e_p2 from the note itself. His m397 calls the
  confirm flag a separate request.
- Night 142 m18, two `conflict` notes about the description
  `executes_commands` on the echo_json page. His m19: "drop them". The
  description ends `draft`.

Counts: **fires on 6 of 6 wrong-request carrier writes, 6 of 42 carrier
writes; refuses 0 of 36 right calls** (observed: `count_out.txt`,
2026-10-16; `request_of` and `page_request` run on each night's final
database, so the request mapping is reasoned to hold at the ruling's
time, because `entries`, `statements` and `refs` of an item do not move).

## 3. The design

**"A request item of the page"** in the rows: an item whose request entry,
`request_of(conn, item)` over `refs` and `statements` to `entries`, is the
page's request, `page_request(conn, ask.refs)` over the page's
`messages.body_refs`. `body_refs` alone does not work: `about_ref` is in
`body_refs` on 0 of 42 fires, so a `body_refs` test kills the carrier and
refuses 36 of 36 right calls. `_is_request_item` does not work either: it
is False for a delivered item and for a description, so it refuses the 33
account cases.

The predicate, in one sentence: the carrier skips a note's `about_ref`
when the page has a request and the item belongs to a different request.

```python
            page_req = page_request(conn, ask.refs)
            other = (page_req is not None
                     and request_of(conn, row["about_ref"]) not in (None, page_req))
            if row["about_ref"] not in ruled and not other and ...:
```

Three landings of the skipped contest:

1. **The contest stays on the note's row.** The `decisions` row
   `overruled at signoff: <words>` and the resolved ledger row are written
   already. The relay takes the note to its author, as m86 did on night
   151. No item of another request moves. "The tool never rules for the
   Principal": he named the note, not `echo_json`, so the tool rules
   nothing for him. "Nothing stops quietly": his words reach the note's
   owner on the relay. Recommended.
2. **The contest goes to the page's own item.** This rules for him on an
   item he did not fault. On m60 he contested lines, not the confirm item.
   It breaks the first line of the composition.
3. **The line returns to him as unplaced.** Nothing is quiet, and nothing
   is ruled for him. It costs one more ask, and his words already placed
   the line ("This page should only cover the confirm flag"). The wall
   cost 3 asks. Option 3 trades them for 1 ask per fire.

Recommend option 1.

**The test file:** `tests/rota/test_signoff_assumptions.py`, beside
`test_a_default_s_contest_reaches_its_item_the_ruling_does_not_name`
(line 331) and the two conflict-note tests (342, 354).

- Red test, from m59, m60 and r_e3e9d2c047: two requests, e_p1 with
  `echo_json` approved and merged, e_p2 with `confirm_default_on_eof`. The
  page carries `confirm_default_on_eof`, `how_it_works` and a Developer
  `default` note about `echo_json`. The ruling revises
  `confirm_default_on_eof`, approves `how_it_works` and contests the note.
  Assert: `echo_json` stays `approved`, the verdict's `body_refs` does not
  name `echo_json`, the ledger row is resolved with an `overruled`
  decision, and the relay carries the note.
- Green tests, kept: the test at line 331 (a default note about an item of
  the page's request); night 136 m165's shape (a note about the page's own
  request item, contested, the item goes `contested`); night 143 m11's
  shape (an account page with no request, a note about a description, the
  description goes `contested`).

## 4. Composition

No. The fix removes a write that no ruling of his made. It changes no
route of who talks to whom, because the relay to the note's owner stays,
and it ships nothing without him. What he sees changes only by the loss
of false asks and a false `Stuck` line, which follow from his own words.

Usage: about 62k tokens.
