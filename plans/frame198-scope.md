# Frame 198 scope read: the agenda tick puts a merged request's open ledger rows on the next request's page

Read-only, Opus, 2026-10-11 14:20, an agent of session be3ef742, 131.3k on the harness line against 100k. The harness refused the report write, so this file is the report as returned. Rota workflow, except the counts and the costs, which are meta workflow. The scripts `q1.py` and `q3.py` and the database copies are under the session's scratchpad, `s198/`.

The uncommitted edits of frame 200's pass 2 in the checkout touch none of this frame's sites. This frame's sites are `scheduler.tick_agenda`, `principal.off_page`, `principal.held_items`, `principal.land` and `lifecycle.merge`. `principal.py`, `scheduler.py` and `lifecycle.py` are clean (observed: `git diff -U0`, 2026-10-11).

## 1. The record: night 139, s264 and m143

The agenda tick s264 had 12 open rows and put the first 7 on m143, because `PAGE_ASSUMPTIONS = 7` (observed: `sessions.wake_detail` and `wake_refs` in `n139p5.db`; `sandbox.py:34`).

| Row | About | Author, session | Reaches | Request |
|---|---|---|---|---|
| `l_2005140716` | `echo_json_no_deps` | Tester s160, woken on bg_1 | `echo_json` | A, `e_p1` |
| `l_22281b299a` | `echo_json_compact` | Tester s160, bg_1 | `echo_json` | A |
| `l_2f6984e1b0` | `echo_json_compact` | Tester s160, bg_1 | `echo_json` | A |
| `l_377a3ee6de` | `echo_json_output_format` | Tester s160, bg_1 | `echo_json` | A |
| `l_a4c7f33ab8` | `echo_json_no_deps` | Tester s160, bg_1 | `echo_json` | A |
| `l_42c21e32c9` | `src/click/utils.py` | Developer s158, woken on bg_1 | no item | A, by the session's batch only |
| `l_2849ed842e` | `cr_1_confirm_eof_default` | Tester s207, woken on bg_2 | `confirm_with_default_on_eof` | B, `e_p2` |

- State at the merge: open, and on no page before m143 (observed: no earlier message holds any of the 7 ids in `body_refs`). bg_1 and bg_2 are `merged`. `lifecycle.merge` (`lifecycle.py:185-247`) writes nothing to `ledger`. A ledger row has two states only, `open` and `resolved` (observed: `schema.sql:552`).
- The other 5 open rows at s264: 3 are request B's, still open, no page has shown them, next in line for an agenda page; 2 are request C's and reach no item, `l_3732f27966` on the term `version_option` by the Terminologist s233, and `l_167e83ebf8` on `tests/test_basic.py` by the Developer s248. Request C's own notes did not sort first, because `reaches_request` reads items only.
- The principal's answer, m144: "Lines 5 to 11 belong to other changes or to test chores and have nothing to do with the Python version flag, so please drop them." s265 ruled all 7 rows `contest`. `land` resolved each row with an "overruled at signoff" decision. Each contest also contested the row's `about_ref`, so verdict m145 named 4 delivered criteria and `src/click/utils.py`. The relay s266 sent these to the Architect (m146) and the Terminologist (m147), and both seats were refused. The cost was 3 sessions and one page off the subject.

## 2. The mechanism

- The query (observed: `scheduler.py:1053-1108`): `tick_agenda` reads `SELECT id, about_ref FROM ledger WHERE status = 'open' ORDER BY rowid`, removes the `reply_rows`, removes a row whose reached items are all in `held_items`, sorts the rows that reach an `open_requests` item first, and takes the first 7. Nothing filters by request. The `agenda` predicate gates on the onboarding phase only.
- Why frame 193's hold passes the rows (reasoned: the code): `held_items` is `aside_items` plus `open_earlier_items`, and `open_earlier_items` (`principal.py:781-813`) skips an item that `_delivered` reports, so a merged item is never held.
- Why the page numbers the rows (reasoned: `principal.py:872-912`): `off_page` keeps a delivered item's note on the page, `if is_note and all(_delivered(conn, i) for i in items): continue`. That is frame 193's design 2.F.7, the answer to finding 4 of its design review. A row that reaches no item stays on every page, by `if not items: continue`.
- The pinned test (observed: `tests/rota/test_frame193_pass2.py:335-337`): "A note about the delivered echo_json item stays a line, so a ruling closes it."
- Nothing closes or parks a ledger row at a merge (observed: a grep for `UPDATE ledger`). Only `land` (`principal.py:1814`) and `_land_shift` (`principal.py:1968`) write `resolved`, both on a principal ruling. `item_parks` parks items, not ledger rows.

## 3. The count on nights 136 to 139

A page counts when it holds a ledger row of an already merged request: a row that reaches only items of a batch that merged earlier, or that reaches no item and comes from a session woken on such a batch (observed: `q3.py`; the merge order from the `do:merge` lines in `.rota/night<N>.log`).

| Night | Merges | Presents | Pages with a merged request's row |
|---|---|---|---|
| 136 | bg_1 `echo_json`, bg_3 confirm | 60 | 20: m159 to m362, 1 to 6 rows each |
| 137 | `echo_json_group` | 19 | 1: m95, 1 row of `echo_json` |
| 138 | b_2, at the end of the night | 28 | 0: no page came after the merge |
| 139 | bg_1, bg_2 | 20 | 1: m143, 7 rows |

Nights 136 and 137 ran before frame 193's 2.F.7, and night 136 before frame 190, so their page rendering differs (reasoned: the commit order). The shape shows on all 3 nights that had a page after a merge. Night 139's 1 of 20 is the baseline.

## 4. The options

The frame's ends-when accepts (a) or (b): "a ledger row of a delivered request is closed or parked at the merge, or the agenda page carries the current request's rows alone". Both options must find a row's request when the row reaches no item, 1 of the 7 rows on m143 and 2 of request C's own rows. The route is `receipts` to `sessions.wake_refs`, or to `checkpoints.batch_id`, and then to `batches.item_id`. A Terminologist row on a term has no batch, so it stays without a request.

| | (a) Park at the merge | (b) The agenda keeps the current request's rows | (c) Both |
|---|---|---|---|
| Files | `lifecycle.merge`; a park record for ledger rows (a new table or a `ledger_park:` config key; a `parked` status needs a change to the schema CHECK); `tick_agenda`; `off_page` or `request_rows`; `render_state` | `tick_agenda` filters `chosen` by request; `off_page` drops the 2.F.7 exception; the send door follows `off_page` already | all of both |
| Tests | new tests on night 139's rows; `test_frame193_pass2.py:335-337` holds, its fixture has no merge | `test_frame193_pass2.py:335-337` flips; check `test_request_page.py:1148` again | both |
| Recorded prompts that move | 0; the one agenda case, `L1-LI-put-the-open-assumptions-to-a-present-principal` (`l1_answers.yaml:355`), has no merge and no request message | 0 expected; one re-record of about 5 runs confirms it | 0 or 1 |
| Opus tokens | an implementer at about 150k to 200k, a review at about 100k | an implementer at about 120k to 180k, a review at about 100k | about 250k, a review at about 120k |
| Walk | one full night | one full night | one full night |
| Risk | Law 8: no page showed these rows before the merge, and a park keeps them off every page. A close writes a decision without a keypress, against DECISIONS. So the option must park, not close | The rows stay open and nothing closes them, frame 193's finding 4 again; the open-row count grows each walk | Both risks, and two mechanisms for one wall |

Recommendation: (a), as a park and not a close (reasoned: the record and section 5). The park takes the rows off the agenda wake and off every later page, keeps frame 193's page rule and the pinned test, moves no recorded prompt, and `render_state` lists the parked rows under the merged request, so the principal can still read them.

One open point, rated [med]: bg_1 shipped with 6 rows that no page showed, and law 8 forbids exactly that. A park accepts this. The recommended answer is to accept it, because DECISIONS of 2026-09-12, point 2, does not let a merge wait on a page.

## 5. Prior rulings

- Law 8 (`rota/LAWS.md:229-232`): "A lineage's open assumptions are presented at its gates: nothing ships whose assumptions the principal never saw" (ruled: LAWS). It says nothing about a page after a merge.
- DECISIONS, 2026-09-03 (`rota/DECISIONS.md:1358-1364`): "a decided row enters the record only from a keypress" (ruled: Roman). Against a close at the merge.
- DECISIONS, 2026-09-12, point 2 (`rota/DECISIONS.md:1384`): "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page" (ruled: Roman). Against a merge gate on open rows.
- Frame 193's design, 2.F.7 and 2.F.9 finding 4 (`plans/frame193-design.md:830-834` and `:853`): a delivered item's notes stay numbered, and a ruling closes them. This is the design review's answer, recorded in the status line of 2026-10-10 04:38 (`plans/archive/stack-2026-10-11.md:16`), not a ruling by Roman. Commit 61a0f41d added the `off_page` exception.
- The `tick_agenda` docstring, from commit 210649a7 of 2026-08-09: "open assumptions reappear at each of their lineage's gates". A merged lineage has no later gate, so the sentence gives no rule for the case.
- `plans/archive/` holds no ruling on what a page carries after a merge (observed: a grep, 2026-10-11).
