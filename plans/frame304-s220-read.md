# Frame 304, the read of s220: the Terminologist could send one answer only

Sources: `.rota/clickI_night158.db` read-only, tables `turns`,
`tool_calls`, `messages`, `rulings`, `criteria`, `tests`, `ledger`,
`sessions`, `batches`. The night databases `.rota/clickI_night140.db` to
`clickI_night158.db`, all 19 present. `rota/core/sandbox.py`,
`rota/roles/api.py`, `rota/core/runner.py`,
`rota/roles/prompts/terminologist/criterion_repair.md` and `.tools`,
`plans/wall-guide.md` section 4, `plans/night158-read.md` row W2,
`plans/stack.md` frames 192, 212 and 304. Branch `rota/foundation` at HEAD
631dcb25. The count script is `f304_count.py` in session 2214bec6's
scratchpad.

## The placement

Step 3 of the wall guide places the sign at cause 1, his words change on
a hop, and the hop is s220's answer m102 (reasoned: section 5). His ruling
r_ce163d8060 marks two criteria, cr_2 `revise` and cr_3 `contest`, and
m101 carries both. m102 carries cr_3 alone, so cr_2's check fix reaches no
seat after s220. The one-answer door does not drop cr_2 by itself. s220
sent cr_3 alone in turn 1, and the door then closed every repair. The
night read placed the sign at cause 10, but the mode holds the call, so
cause 10 does not fit (observed: `criterion_repair.tools` lists
`msg.answer_tester`). The recommended end is a new frame.

## 1. s220's turns 1 to 5

- The relay m101 from the Liaison woke s220 in mode `criterion_repair`.
  Its refs are cr_2 and cr_3, and `principal_verdict` is cr_2 `revise`,
  cr_3 `contest` (observed: `turns` s220 seq 1, `user`).
- The block "[the principal contested these criteria]" names cr_3 alone,
  twice. cr_2's `revise` shows only in the JSON (observed: the same text).
  `_relay_contest_block` keeps only `contest` rows (observed:
  `rota/core/runner.py`, `_relay_contest_block`).
- Turn 1: `criteria.respecify` of cr_3 with surface `termui.py::prompt`,
  and `msg.answer_tester` with refs cr_3 only (observed: `tool_calls`
  seq 10 and 11).
- Turn 2 shows the respecify refused, "The item asks for `confirm`, and
  this move drops `confirm` from the surface." The answer landed: "OK
  msg.answer_tester -> {"id": "m102", "to": "tester", "verb": "answer"}"
  (observed: `turns` seq 2, `user`). The doors judge each call alone, so a
  send lands beside a refused write.
- Turn 2's reply: the same respecify with surface `confirm`, and the same
  answer. Turn 3 shows the respecify landed and the answer refused: "you
  have already sent answer to tester; saying it again with different refs
  is a second answer to one question, and the recipient has to reconcile
  them. Your work here is done" (observed: `turns` seq 3).
- Turn 4 repeats turn 3's refusal (observed: `turns` seq 4).
- Turn 4's reply: `criteria.respecify` of cr_2, and `msg.answer_tester`
  with refs cr_2 and cr_3 (observed: `tool_calls` seq 16 and 17).
- Turn 5 shows two refusals. The cr_2 respecify: "the principal faulted
  the check and not these words: ... The criterion stands. Send his words
  about the check to the Tester with msg.answer_tester, with this
  criterion in refs." The answer: the same one-answer refusal, then "NOTE
  msg.answer_tester has been refused the same way in three turns and will
  not be accepted again" (observed: `turns` seq 5).
- Turn 5's reply: `ledger.log` of kind `fault` on cr_2, refused, and the
  answer again. Turn 6 ends the session: "msg.answer_tester was refused
  the same way in four turns; the session ended on it" (observed:
  `turns` seq 6).

The cr_2 refusal names `msg.answer_tester`, a call the one-answer door
refuses at that moment (reasoned: turn 5). That is the cause 9 shape, and
it breaks the rule that a refusal names a call only where the doors admit
it (observed: wall guide, cause 9, cheap fix).

## 2. The door and its origin

- The door is not in `rota/roles/api.py`. It is in `_bind_send` in
  `rota/core/sandbox.py`, about line 3747, on `_sent_this_session` at
  line 1491 (observed: grep of the refusal text).
- The predicate matches recipient and verb, not refs (observed:
  `_sent_this_session`).
- Commit b41626d1 of 2026-08-14 00:49 +0100 made it so (observed: `git log
  -S`). Its comment: "Matching on refs too caught the exact repeat and
  missed the expensive one: Terminologist answered a Developer's question
  correctly, then sent the same answer again with one ref added, then
  again with it removed."
- The same comment says: "A role with two genuinely separate things to say
  to the same role says them in one message's refs, which is what refs
  are" (observed: b41626d1).
- The commit names no ruling of Roman's. It is the session's reasoning
  (observed: the commit body). It predates the relay of a ruling to the
  Terminologist, so no ruling on two criteria was in view (reasoned:
  `criterion_repair.md` gained its ruling paragraph on 2026-10-13,
  33cd99b2).
- The repair brief says "For each criterion with contest or revise ...
  send `msg.answer_tester` with the criterion in `refs`" (observed:
  `criterion_repair.md`). "For each" invites one send a criterion, and
  the door admits one send a session (reasoned).

## 3. What reached s221, and after

- m102 carries refs cr_3 only, verdict cr_3 `contest`, and his words in
  full (observed: `turns` s221 seq 1).
- cr_3's text in m102 is s220's rewrite, "When confirm() shows its prompt
  and attempts to read from stdin ... without emitting any error message"
  (observed: the same). He said to drop that line, and no seat dropped it.
- s221 encoded only cr_3's test, `tst_confirm_eof_03` (observed:
  `tool_calls` s221 seq 8 to 11). Its ledger note shows it read "fix line
  4 (fake closed input properly)" and did not act on it (observed: ledger
  `l_3eb9355378`).
- No message after m101 and no later tool call names cr_2 or
  `tst_confirm_eof_02` (observed: `messages`, `tool_calls`). That test
  stays at version 3, the broken stub, and bg_2 ends `deferred`
  (observed: `tests`, `batches`).
- The second criterion of m98 reached no seat after s220 (reasoned: the
  four rows above).

## 4. The count over nights 140 to 158

- Terminologist sessions: 934. Sessions refused for a second answer: 76
  (observed: `f304_count.py`, refusal text in `turns.user`).
- Of the 76, 20 woke on a relay whose ruling marked two or more criteria
  `contest` or `revise` (observed: the same, ruling by `verdict_id` or
  `reply_id`). All 4 partial answers among 72 such relays drew the refusal.
- Of the 20, 4 sent an answer that omitted a ruled criterion: night 142
  s431 (cr_1), night 157 s191 (cr_3) and s362
  (`crit_show_python_version`), night 158 s220 (cr_2) (observed: the
  same).

## 5. The placement by section 4, and the end

1. Is the sign an open frame's sign? No. Frame 304's mechanism is the
   encode door. Frame 212 is the Architect. Frame 192 is the `drop` word
   (observed: `plans/stack.md`). The residue rule asks a new frame when
   the cause differs (ruled: Roman, 2026-10-03).
2. Is the instrument right? Yes. `tool_calls` and the `turns` text agree
   on every call and refusal (observed: section 1).
3. Does the sign name his words? Yes, the second criterion of his ruling.
   The first hop that differs is m102, so cause 1 places it (reasoned:
   section 3). The step stops here.

Two shapes sit at that hop. cr_2: the seat sent part of the ruling, and
the door made the omission final (reasoned: section 1). cr_3: his "Drop
line 5" has no criterion call in the mode, so s220 rewrote it (observed:
`criterion_repair.tools`). The cr_3 shape is frame 192's word, not this
sign.

The three ends:

- A recorded case under the existing register: no. Cause 1's "Not now,
  when" is "Never", and the effect reaches a page (observed: wall guide).
- A part of frame 304's pass: no. That pass is a cause 8 door on
  `tests.encode`, a different site and cause (reasoned: step 1).
- A new frame: recommended. Its Ends-when:
  1. The mechanism: the Terminologist's answer to a ruling relay carries
     every criterion ruled `contest` or `revise`, with s220's turn 1 as
     the red test, and no refusal names a refused call.
  2. On a night: partial answers to a ruling relay, 4 of 20 over nights
     140 to 158, toward 0 over the next 3 nights.
  3. A session that still omits one is read, and the cr_3 `drop` shape
     goes to frame 192 as a case.

The reason: the cause is cause 1 at the Terminologist's hop, so the
residue rule asks a new frame. The count shows 4 lost criteria in 19
nights, and cause 1 permits no "not now". The design choice stays open:
refuse a first answer that omits a ruled criterion, or admit a second
answer on relay refs not yet sent (reasoned: section 2).
