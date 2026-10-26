# W-B and W7, the provenance read: the naming door reads his last answer only

Date: 2026-10-26, read at 19:20 to 19:40. Read at commit 2f7496be on
`rota/foundation`, dated 2026-10-26 19:37. The code read is the same at
88464039, because the commits between them touch `plans/stack.md` only.
Read-only. The night databases were opened with `?mode=ro`. No model call
ran and no pytest ran. Meta workflow for the read, by the rule of
2026-10-18 (provenance before a fix). Sprint 25, row 5.

Sources:

- The symptom records, cited and not repeated: `plans/night168-read.md`
  section 1, walk 2 (line 77 on), section 2 row W7 (line 110), question 5
  (lines 183 to 195), and the fix list row 5 (line 277);
  `plans/night166-read.md` row W-B (line 210) and the fix list row 4 (line
  367).
- `rota/roles/api.py`: `rulings_rule` 12389 to 12841 (the call of
  `_line_refusal` 12779), `_line_refusal` 11766 to 11858 (the call of
  `_unnamed_contest` 11807), `_unnamed_contest` 12137 to 12180.
- `rota/core/runner.py` 2640 to 2660, the writer of `earlier_exchange`.
- `rota/roles/prompts/liaison/landing.md` lines 11 to 24 and 49 to 51.
- `rota/LAWS.md` lines 183 to 193 (law 6). `rota/DECISIONS.md` lines 1445
  to 1476 (the ruling of 2026-10-08, point 4 at 1473) and 1397 to 1416.
- `plans/archive/stack-2026-10-15.md` line 5 (frame 234).
  `plans/stack.md` line 1778 (frame 266) and
  `plans/archive/stack-2026-10-17.md` line 110 (frame 267).
- `.rota/clickI_night168.db`: `messages` m75 to m78, `sessions`, `turns`
  and `tool_calls` of s191 to s194, `rulings` r_448c39118c.
- `.rota/clickI_night160.db` to `.rota/clickI_night168.db`, 10 files:
  `sessions`, `turns`, `messages`, `rulings`. The count script is
  `wb_count.py` in the scratchpad of session ac089aa1.
- `git log -L` on `_unnamed_contest`. `git log -S` on `def _unnamed_contest`,
  `A contest rests on the principal's words`, `Approve the lines the words
  do not name`, `landing["earlier_exchange"]`, `the whole reply as` and
  `A session on this reply ended with no ruling`.

## The result

**Verdict: a gap, not a departure. The naming door was built on 2026-10-14
for one reply against one page, and nobody named what a contest rests on
when the reply is the second answer of an exchange, so the door reads the
`words` argument alone, and the brief fills that argument with the last
reply alone.** The design of 2026-09-10 put the exchange in the prompt so
that the Liaison rules on the whole exchange after an ask (observed:
b57772f5, `landing.md` lines 21 to 24). Frame 234 pass 2 added the door on
2026-10-14, measured on single replies of nights 143 to 147 (observed:
250f3806). The door never reads `earlier_exchange`, and its refusal tells
the seat to "Approve the lines the words do not name" (observed: `api.py`
12177 to 12180). Frame 267's second wake then carries that refusal to a
fresh session, which approves (observed: 0582873a, s194's head). The
outcome breaks law 6 and the ruling of 2026-10-08, and the repair restores
both, so no choice is left for Roman (reasoned: section 5).

## 1. Which design made the door read the last answer only

- The door: 250f3806, 2026-10-14 19:55, "fix(liaison): the verdict door
  refuses a contest on a line the principal's words do not name", frame 234
  pass 2 (observed: `git log -S "def _unnamed_contest"`, its body). The
  case was night 147's m131, one reply that faulted lines 3, 4 and 7 while
  the Liaison contested six more. The measure was "13 over-contests and 0
  right rulings" on the recorded replies of nights 143 to 147 (observed:
  the commit body). No case in that measure was a second answer after an
  ask (reasoned: the body names single replies only).
- The refusal text "The words name ... and do not name ... A contest rests
  on the principal's words. Approve the lines the words do not name" comes
  from the same commit (observed: `git log -S` on both phrases). The phrase
  "and do not name" first appears in f7b8fc7e of 2026-10-13, in another
  door (observed: `git log -S "and do not name"`).
- The commits since, by `git log -L`: 91d8fcc3 and 0ad6e7c3 of 2026-10-14
  (an unnumbered sentence spares an item line only), f0b2924c of 2026-10-16
  (the approve of a faulted line), e445aa64 of 2026-10-16 (a contest lands
  only on a line the words name, measured over 72 nights), 42a4449e of
  2026-10-17 (a range ends at the page's last line), c5de8a2f of 2026-10-18
  (the law comment). None of them reads the exchange (observed: the
  `git log -L` output and the current body).
- The input: the door reads `words`, the argument the Liaison passes, and
  no check compares it with any message (observed: `rulings_rule`, no read
  of the trigger's `body_text`). The brief says "the whole reply as
  `words`", and `reply` is the last message alone (observed: `landing.md`
  lines 11 to 13 and 49, from b57772f5).
- `earlier_exchange`: b57772f5, 2026-09-10 03:09, "feat(seat): the
  principal's words land through the Liaison, not a parser" (observed:
  `git log -S 'landing["earlier_exchange"]'`). It was for the ask path: "The
  page stays open, and their next reply comes back here with this exchange
  in `earlier_exchange`" (observed: the brief text of that commit). Frame
  142 later added the Liaison's own questions, marked `asked` (observed:
  `runner.py` 2640 to 2644).

## 2. What the door should read

- A contest may rest on any answer he gave to the open page. The ruling of
  2026-10-08 says: "Every word of the principal is a ruling on a row, or it
  earns one Liaison question that names a row" (ruled: Roman, 2026-10-08
  23:25, `DECISIONS.md` 1473). An answer that earns a question still owes
  its ruling, so the second answer does not cancel the first (reasoned:
  the ruling's "or" admits the question, and it does not drop the words).
- Law 6 forbids an approve the words refuse: "It is never a ledger row
  written on the principal's behalf" (ruled: 2026-09-13, `LAWS.md` 188).
- The design of 2026-09-10 makes the exchange the reading unit after an
  ask (observed: b57772f5, `landing.md` 21 to 24). The page is the frame of
  reference, and line numbers name page lines (observed: `_unnamed_contest`
  reads `_LINE_REF` against `size`).
- Frames 266 and 267 do not rule on what a contest rests on. Frame 266 is
  the call parser's refusal text (observed: `stack.md` 1778). Frame 267
  makes a reply with no ruling wake one more session and then return the
  page (observed: `stack-2026-10-17.md` 110, 0582873a). Frame 267 is the
  path that carried the door's refusal to s194 (observed: s194's head).
- A contest that rests on an earlier answer of the same exchange falls on
  a default nobody named. The door's author measured single replies, and
  the brief's "the whole reply" predates the door by five weeks (reasoned:
  sections 1 and 3).

## 3. What the records show

- m75: the page, line 5 is `challenge_items_clear_returns_status`, line 6
  is `l_c5331791cf` (observed: s193 turn 1, `landing.lines`).
- m76: "Line 5 is wrong: ... I don't understand line 6, so what is that
  ticket ... The other lines are fine." (observed: `messages`).
- m77: the Liaison's question about line 6 (observed: `messages`).
- m78: "... so line 6 is fine as it stands." It names line 6 only
  (observed: `messages`).
- s193 calls 1 and 2: `{1 to 4: approve, 5: contest, 6: approve}` with
  `words` = m78, refused twice "The words name line 6 and do not name line
  5", then ended on the verbatim repeat (observed: `turns` 1 to 4).
- s194's head: "A session on this reply ended with no ruling. Its last
  refusal or error: ... Approve the lines the words do not name" (observed:
  s194 turn 1).
- s194: one call, every line `approve`, `words` = m78 (observed: `turns`).
- r_448c39118c: landed, reply m78, six rows `approve`, line 5 among them
  (observed: `rulings`).
- **Yes, s193's prompt held m76 in `earlier_exchange`, with m77 marked
  `asked`** (observed: s193 turn 1, `user` from character 8150).

## 4. How often

Over 10 night files from night 160, 43 naming-door refusals ran in 24
Liaison sessions. 14 of them quote a line that his earlier answer in the
same exchange names (observed: `wb_count.py`, line references by the door's
own `_LINE_REF`).

| Night | Refusals | Earlier answer names the line | The exchange then approved that line |
|---|---|---|---|
| 160 to 164a | 19 | 0 | 0 |
| 165 | 7 | 2 (s318, line 9, m173) | 2 (r_df7c82685f, on m183) |
| 166 | 6 | 6 (s109, s110, line 3, m25) | 0 |
| 167 | 7 | 4 (s99, s100, line 6, m12) | 4 (r_38a452d55c) |
| 168 | 4 | 2 (s193, line 5, m76) | 2 (r_448c39118c) |

- 3 of the 4 exchanges ended with an approve of the line, and 8 of the 14
  refusals (observed: the table).
- 2 of the 3 approves are against his words. Night 167's m12 says of line 6
  "please remove it", and night 168's m76 says "Line 5 is wrong" (observed:
  `messages`). Night 165's m173 describes line 9 and does not clearly
  fault it (reasoned: its text).
- The shape is four nights old and on every night since 165 (reasoned: the
  table). "Names" counts any reference, a fault or not (reasoned: the
  method).

## 5. Whether a design departure stands

The rulings that cover what a contest rests on are the ruling of
2026-10-08, "Every word of the principal is a ruling on a row" (ruled:
Roman, 2026-10-08 23:25, `DECISIONS.md` 1473), and law 6 (ruled:
2026-09-13). The build did not choose to depart from them. It left the
exchange out when frame 234 built the door on single replies, and the
outcome of r_448c39118c and r_38a452d55c breaks both (reasoned: sections 1
to 4). The repair restores the ruling as written, so no question for Roman
stands (reasoned: the rule of 2026-10-25 asks on a departure from his
ruling, and the repair does not depart).

## The repair

`rulings_rule` reads the lines his earlier converse answers to the same
page name, with the query `runner.py` uses for `earlier_exchange` and
principal rows alone, and passes them to `_unnamed_contest` in `read`. A
contest of such a line then lands, and the owner's `words` carry the
earlier answer beside the last one. A line that no answer of the exchange
names stays refused, as frame 234 built it.

Red test, from night 168's rows: s193 turn 1, `{1 to 4: approve, 5:
contest, 6: approve}` with `words` = m78 and m76 in the exchange, lands
with line 5 `contest` and no refusal. Green guard: night 147's s281 case,
one reply with no earlier answer, stays refused.

## Usage

One agent on Opus, about 60k tokens of context. Not read: what the approve
of `challenge_items_clear_returns_status` did to the item; the full text of
night 165's m183, the reply that landed r_df7c82685f.
