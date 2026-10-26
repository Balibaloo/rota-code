# Frame 338, the agency read: the relay split reads the verdict map and not the ruling

Date: 2026-10-26, read after 21:00 at 46e5c88b on `rota/foundation`. Read-only. No pytest and no model call ran. Nine night databases, 160 to 168, were copied to this agent's scratch folder and opened with `?mode=ro`. The read called `park_criterion_relay` on those copies. Meta workflow.

## Verdict

**At one door of 3.** The built fix 6876a7e5 covers the approved test row on a verdict. It leaves the approved criterion and the approved test row on a converse reply, because the split reads the verdict map only (observed: sandbox.py 4486 to 4500). Night 164's m94 lost his contest of two criteria by that open door (observed: question 3).

## 1. The purpose

The relay split routes each ref of a ruling's relay to the single writer of its table. It started in 84ea995f of 2026-08-26, "observed gets its exit", so that each owner adopts the rows the principal approved (observed: the commit body). The same commit made the relay take every ref of the trigger, because the Liaison relayed one of two rows, five runs of five (observed: sandbox.py 4140 to 4156). The approve filter for a criterion came in 4ef3bd9f, 2026-10-09 03:00, frame 142 pass 2b, from the diff review of 0baacf55, finding 2. Frame 190's design, 2.F amendment 1, widened it to every page (observed: sandbox.py 4486 to 4500; frame190-design.md 822). The test-row branch came in 1055a2c5, 2026-10-13 16:46, frame 213 route B, to serve his ruling of 2026-10-08 23:25 that the Tester rewrites a test from the ruled words (observed: git log; ruled: Roman, DECISIONS.md 1459 to 1465). The Site line names `park_criterion_relay` in runner.py. The function is in scheduler.py 2009 (observed: grep).

## 2. What exists

| Thing | Where | What it holds |
|---|---|---|
| The relay widening | sandbox.py 4145 to 4156 | adds every ref of the trigger, approved rows too, by design for adopt (84ea995f) |
| The clarify widening | sandbox.py 4160 to 4173 | adds the contested and revised rows of a `rulings` write staged this session |
| `verdict_rows` | scheduler.py 1949 to 1967 | contest and revise rows from `config` `verdict:<id>` only, None on any trigger that is no verdict |
| `ruled_test_criteria` | scheduler.py 2065 to 2096 | the verdict map, else the landed `rulings` row by `reply_id` or `verdict_id` |
| `ruled_clarify_criteria` | scheduler.py 2039 to 2062 | the landed `rulings` row of a clarify reply, criteria only |
| The park filter | sandbox.py 4491 to 4493 | drops every row the park verdict does not contest or revise |
| The off-park filter | sandbox.py 4494 to 4500 | drops an approved criterion, on a verdict trigger only |
| The test-row guard, 6876a7e5 | sandbox.py 4527 to 4532 | drops an approved test row when `ruled` is not None |
| The mode key | scheduler.py 2009 to 2036 | `criterion_repair` only when every ref is in the ruled set of three readers |
| The `rulings` record | the `rulings` table, `per_item` | his ruling on a verdict and on a converse reply, one record (ruled: composition.md, "A ruling is a record") |

The split and the key derive one fact, the rows his ruling contests, from different records. The split reads the verdict map. The key reads the verdict map and the `rulings` row (observed: the table). Wall guide section 4, step 5, names this shape: two records about one fact, cause 12 (reasoned).

## 3. The reach

The cause the frame places: an approved row enters the relay through the widening, the split keeps it, and the all-refs key then sends the relay to `relay` mode, where no call reaches the Tester (observed: c3-relay-provenance.md, the result). The code shows three places with that gap, and one scene.

1. **An approved test row on a verdict.** sandbox.py 4520 to 4532. Observed on 6 relays: m50 and m57 of night 168, and m53, m59, m161 and m165 of night 167. In each one the Liaison named only the contested rows, and the widening added the approved ones (observed: `tool_calls` of s151, s158 and s156; `config` `verdict:m52`, `verdict:m58`, `verdict:m160`, `verdict:m164`).
2. **An approved criterion on a converse reply.** sandbox.py 4494 to 4500 runs only when `verdict_rows` is not None, so a clarify reply's relay keeps every approved criterion. Night 164's m94 carried cr_1 to cr_6. The ruling r_35e06b1383 contests cr_2 and cr_6 and approves four. The key on HEAD is false, s195 called `glossary.adopt` twice, and no call acted (observed: the copy of night 164; `park_criterion_relay(m94)` on HEAD). In the same 9 nights, 11 more clarify relays carried approved criteria only and woke a Terminologist that could do nothing: night 160 m63; 161 m39, m58, m129, m173; 162 m34, m133, m196; 165 m74, m127, m198 (observed: the copies).
3. **An approved test row on a converse reply.** sandbox.py 4527 to 4532. On a converse trigger `ruled` stays None, so the guard of 6876a7e5 does not run. A test row does reach a clarify relay: night 144's m400 (observed: scheduler.py 2075 to 2077). No case on nights 160 to 168 (observed: the scan).
4. **A scene.** tests/rota/test_frame306_clarify_about.py 202 to 210 writes a clarify relay of an approved criterion by hand and asserts the key only. The proposal below keeps it green (reasoned).

Count: 3 code instances and 1 scene. Not counted, with the reason:

- Night 161's m197, the seventh relay of the provenance count, is another cause. Its ref c_2 is a criterion row and no line of page m191, so the split gave it the plain Terminologist key. Its sibling m198 carried the ruled criteria and s362 called `msg.answer_tester` five times (observed: the copy of night 161).
- The approved item that the off-park filter sends to the Vision Keeper (frames336-338-review-p1.md, finding 4). The item has an act for an approve, the adopt of an observed row (observed: 84ea995f body; night 160 m5). Whether an approved decided item is the same gap needs that frame's read (reasoned).

## 4. The fix against the reach

The built fix covers instance 1, 6 of the 7 observed relays of the provenance count (observed: the diff of 6876a7e5). It leaves instance 2, with one observed loss of two contested criteria and 11 empty wakes. It leaves instance 3, which has no observed case. The guard reads `ruled`, and `ruled` comes from `verdict_rows`, which is None on a converse trigger (observed: sandbox.py 4486 to 4495). The frame's second Ends-when, from 2 of 2 toward 0 of the next 3, counts relays of a ruled test row only. It does not see instance 2 (observed: the Ends-when line).

## 5. My proposal

Not the same fix. The guard is right and stays. The source is the reader of `ruled`, one place above both filters.

1. Add `ruled_rows(conn, message_id, writes)` beside `verdict_rows`. It returns the verdict map's contest and revise rows, else the landed `rulings` row's, else a staged `rulings` write's, else None (scheduler.py 1958 to 1967, 2079 to 2087; sandbox.py 4160 to 4173).
2. In the split, take `ruled` from `ruled_rows` in place of `verdict_rows`, so the criterion filter and the 6876a7e5 guard run on a converse reply too (sandbox.py 4494 to 4500, 4527 to 4532).
3. Keep the widening and the mode key. The widening serves the adopt of approved observed rows, and the key's reason, a term beside a criterion, still holds (84ea995f; 172b373b body).
4. Derive `ruled_test_criteria` and `ruled_clarify_criteria` from `ruled_rows`, so the split and the key read one record (composition.md, Records; wall-guide.md section 4, step 5).
5. Red tests from the rows: night 164's m94 gives a relay of cr_2 and cr_6 that keys `criterion_repair`, and a clarify with an approved test row gives no criterion. Night 168's m50 test stays green (frames336-338-review-p1.md, point 3).

Price: 2 cycles, about 20k of the holding session. One implementer pass resumed on Opus, about 24k to 40k, and one review, about 61k to 76k (operating-facts.md, cost anchors and the cycle line 247). Change the second Ends-when to count every relay whose ruling contests a row and ends with no acting call, verdict and converse alike.

## 6. The doubt

- A clarify relay of approved criteria only would then be refused at the Liaison with "approved these criteria as they stand". I did not check whether the Liaison stops there or loops on the refusal.
- I did not read when the `rulings` row of a converse reply is committed against the split, so the staged-write branch of line 1 rests on the clarify widening's use of `ctx.writes`.
- I did not check approved `guess:` and batch refs, which also pass the off-park filter and key their own modes by an all-refs test.

## Usage

One agent on Opus, no sub-agent. Read: the frame block, c3-relay-provenance.md, frames336-338-review-p1.md, the diff of 6876a7e5, sandbox.py 4135 to 4580, scheduler.py 1900 to 2096, the commits 84ea995f, 4ef3bd9f, 1055a2c5 and 172b373b by log, composition.md Records and Flows, wall-guide.md section 4, operating-facts.md cost anchors.
