# Frame 316 with 315, W3 of night 163: review of 80f7d211

Reviewer: read-only, worktree C:/Users/roman/rota_r316w3 at 80f7d211. I ran no gate, no model and no replay. I edited no tracked file.

Result: the change stands with fixes. Hop 1 fixes m48 on the night's data. Hop 2 does nothing on the night's data, because night 163 had one request and not two. The cause of point 5 is a supersede link that s146 wrote, and no hop touches it.

## (a) Verdicts

1. Holds, by hop 1 only. On the night's rows, the page keeps item 3's rows, and item 1's item, criteria and guess leave. Hop 2 drops nothing on the night's rows (finding 1).
2. The limit is a proxy and not the rule. Two shapes still abandon the item: the night's own shape (one request because of the supersede link) and an all-approved page (finding 1, finding 2).
3. The drop is silent. The result text, the ledger and the page show nothing. Only `tool_calls.args_summary` keeps the six refs the model sent (finding 3).
4. A paste with one or two words changed is refused. A third-person rewrite is refused. A sentence plus one more sentence is refused. A legitimate item text taken from his reply is refused when no statement holds it yet (finding 4).
5. `off_page` kept item 1's rows because both items belong to request e_p1. s146 segmented s2 (the clear request, e_p3) with `supersedes='s1'`. `current_request` then treats m_p3 as a follow-up, and `request_of` roots s2 at s1 (finding 1).
6. Holds on the diff. No prompt file changed. I did not re-run the LI and VK replays. I rely on the implementer's count of the same 4 reds on the old and the new code.

## (b) Findings

1. rota/roles/principal.py:1998, high, CONFIRMED. Hop 2 compares `request_of` of the contested item with the page's request. On the night's rows both are e_p1, so `_drop_other_request_contests` drops nothing from m48's real `per_item`. The probe set the m48-time approvals (item 1 approved, item 3 draft). The result was "dropped: []". With `statements.supersedes` of s2 set to NULL, the same call drops c_1, c_2, format_filename_example and guess:format_filename_example. The test fixture (tests/rota/test_frame316_w3.py:49-65) gives s2 no supersede link, so it tests a shape that the night did not have. The cause is s146's `brief.segment(id='s2', span_entry='e_p3', supersedes='s1')`. That call joins an unrelated new ask to the format_filename request. Fix: refuse a `brief.segment` supersede whose new statement shares no subject with the statement it supersedes, or let a new request message always start a boundary. Then add a test on the night's supersede shape.
2. rota/roles/principal.py:1984, medium, PLAUSIBLE. The `asks` condition fires only when the page asks about a draft or contested item of its own request. A page whose own items are all approved, such as an agenda page or a re-present after an all-approve, keeps the old abandon for another request's approved rows. The condition exists to keep test_request_page green (deviation 2). The rule it stands for is "a row this page does not number for its request". Fix: drop the contest when the row is in `off_page(conn, ask.refs)` at land time, and keep the draft exception from the frame 190 design explicit.
3. rota/roles/api.py:779-795 and rota/core/sandbox.py:3671-3674, medium, CONFIRMED. The probe called `msg.submit_liaison` with six refs on a wake that named item 3. The result was `{'id': 'm1', 'to': 'liaison', 'verb': 'submit'}`, the message carried one ref, and the ledger had 0 rows. The seat is not told which refs left, and no reader of the messages sees the drop. Fix: add the dropped ids to the result text, for example a "dropped" key that names each item and the reason.
4. rota/roles/api.py:1497-1576, low, CONFIRMED. On a signoff wake for item 3, the text "For clear(), the output stays the same and only the return value changes." from m49 is refused as the text of clear_returns_bool. That sentence is his correct ask for item 3, and s3 holds it only later. The refusal says "it is not the text of clear_returns_bool", which is false. Law 11 supports the refusal, but the wording misleads the seat. Fix: say that no statement holds the sentence yet, and name `msg.report_liaison` as the step.
5. rota/core/sandbox.py:3673, low, PLAUSIBLE. The present filter drops only refs in the `items` table. A Liaison that names c_1, c_2 or guess:format_filename_example directly keeps them on the page. `off_page` keeps them too while the supersede link of finding 1 stands. s152 named items only on the night, so the night does not show it. Fix: filter each ref whose `_items_reached` set holds no submitted item.

Outside the points: finding 1's supersede link also makes `current_request` return m_p1 as the current request on the whole night. Every reader of request boundaries (`held_items`, `open_earlier_items`, `page_request`) then reads one request where he made two. This is likely part of W3's six contested sessions and of the "You asked" pages m70 and m92. Read it before the next fix.

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e7141541-fc20-4c5c-a91b-4a10a610ec42/scratchpad/n163w3/. Each night probe ran on probe.db, a copy of D:/repos/rota/.rota/clickI_night163.db with its WAL, and rolled back.

- q1.py: read m47, m48, m49, m61, the items, the submits and the m48 ruling. s151 and s152 tool calls read with `python -c`.
- p5.py: `current_request` gave m_p1. `page_request(m48)` gave e_p1. `request_of` gave e_p1 for both items. `off_page(m48)` gave the empty set. statements showed s2 with `supersedes='s1'`, written by s146 `brief.segment`.
- p2.py: hop 2 on m48's real `per_item` dropped nothing. With s2's supersede set to NULL, it dropped four item 1 rows.
- p1.py: `request_rows` and `code_targets` on the hop 1 refs gave item 3's rows and `guess:clear_returns_bool` only.
- p3.py: the submit drop on the test fixture. The result text and the ledger showed no drop.
- p4.py and p4b.py: `_reply_sentence_fault` on seven variants of m61 and on m49's clear sentence for item 3.

## (d) Usage

About 45k input tokens and about 9k output tokens, about 54k in total. These are estimates. The harness gives no exact count.

Stands: 80f7d211 stands for m48 through hop 1. Hop 2 needs findings 1 and 2 before it protects the night's shape. The supersede link of finding 1 is the open cause.
