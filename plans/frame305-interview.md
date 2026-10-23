# Frame 305, the interview of s209 turn 1: the Liaison took m62's "Line 2 is wrong" from `recent_chat` as a fault of page m89's line 2

## The result

The seat read "Approve 2" as line 2. It contested line 2 on words of m62,
a reply to the earlier page m61, where line 2 was `cr_1` (observed: the
interview below, and `messages` m61 and m62). The prompt does not say
which page each `recent_chat` reply answered. So the wall places at
cause 2, not at cause 4 or 5 (reasoned: section 4 below). Neither probe
moved the seat: (a) 0 of 3, (b) 0 of 3 (observed: the probes below).

## 1. The turn and what the prompt held

- Night 158, `.rota/clickI_night158.db`, session s209, role liaison,
  `qwen3:8b`, temperature 0.0, `num_ctx` 16384, turn 1 of 3 (observed:
  `sessions` and `turns`).
- The head: "A session on this reply ended with no ruling. Its last
  refusal or error: rulings.rule: the words do not fault the code of
  confirm_default_on_eof. Approve 2." (observed: s209 turn 1 `user`).
- The page m89 numbers 1 the request, 2 the guess, 3 to 5 `cr_1` to
  `cr_3`, 6 to 8 the glossary terms (observed: `landing.lines`).
- `line_rows` holds rows for lines 1 and 3 to 8, and no row for the guess
  line (observed: the same).
- The reply m90 names line 5 and the checks of lines 4 and 5 (observed:
  `landing.reply`).
- `recent_chat` holds eight earlier messages. Two start with a line number:
  m51 "Line 2 is wrong: the change lives in confirm() itself ...", and m62
  "Line 2 is wrong: today confirm() raises Abort at end of file, not
  UsageError ...". No entry names the page it answered (observed:
  `recent_chat` in s209 turn 1).
- m62 answered page m61. On m61, line 2 is `cr_1_confirm_default_on_eof`,
  and line 1 is the request (observed: `messages` m62 `cause_id`, and the
  `lines` of s166's landing on m62).
- The recorded call: `{1: approve, 2: contest, 3: approve, 4: contest,
  5: contest, 6: approve, 7: approve, 8: approve}`, the same map as s208
  (observed: `turns` and `tool_calls` of s208 and s209).

## 2. The interview, verbatim

The tool: `probes/frame37/interview_turn.py --db .rota/clickI_night158.db
--sid s209 --seq 1`, its default model and temperature, think off. The
tool sends the four questions in one call after the turn (observed: the
tool's source). Three runs gave the same answers word for word, at 7s,
2s and 2s, 172 output tokens each (observed: the runs, 2026-10-23).

The answers of all three runs:

> 1. The "Approve 2" refers to line number 2, indicating that line 2 was
>    approved.
>
> 2. The principal's words that faulted line 2 were: "Line 2 is wrong:
>    today confirm() raises Abort at end of file, not UsageError, and the
>    flag should default to False so existing callers see no change."
>
> 3. Line 2 looked like a code line. I knew this because it was labeled as
>    "guess:confirm_default_on_eof" and it described a change to the
>    confirm() function, which is code-related.
>
> 4. If line 2 had been revised to correctly state that the flag should
>    default to False and that confirm() raises Abort at end of file, then
>    lines 4 and 5 could have been contested for their specific issues,
>    while line 2 would have been approved.

**The answers read against the record.**

- Answer 1: the seat read a line number, not a key (observed: answer 1).
  It reads "Approve 2" as a report, "line 2 was approved", and not as a
  step (reasoned: the word "indicating").
- Answer 2: the quote is m62 word for word, from `recent_chat`. m62's
  "Line 2" is `cr_1` on page m61, not the guess on page m89 (observed:
  section 1). The record confirms the quote is in the prompt.
- Answer 3: the seat names the guess id and calls line 2 a code line.
  That matches the page, where line 2 is "The team's plan of the code"
  (observed: the page text). The missing row did not hide what line 2 is.
- Answer 4: the seat wants line 2 changed to meet m62. So it still holds
  m62 as a correction of this page's line 2 (reasoned: answer 4 against
  answer 2).

## 3. The probes

The probe sends s209 turn 1 through `llm.OllamaBackend.complete`, the
runner's own call, with the session's pins and the text protocol
(observed: `rota/core/runner.py` 4168 to 4169, 4311). The right call is
line 2 approve, lines 4 and 5 contest, the rest approve. The script is in
the session's scratchpad, `f305_probe.py`.

**Control, 1 run.** `{1, 2, 3, 4, 5: contest}`, lines 6 to 8 left out.
The control does not repeat the recorded map, but line 2 is contest as
recorded (observed: the run, 2026-10-23).

**(a) The refusal sentence replaced by the offered call: 0 of 3.** The
head read "Its last refusal or error: rulings.rule: TOOL:
rulings.rule(rulings={1: "approve", 2: "approve", 3: "approve", 4:
"contest", 5: "contest", 6: "approve", 7: "approve", 8: "approve"},
words="<the m90 reply>")". All three runs sent the recorded map, line 2
contest, and wrote `8: "approve}` with the closing quote lost (observed:
the runs).

**(b) A guess row in `line_rows`, marked `"kind": "guess"`: 0 of 3.** The
row holds the page's own text of line 2 and sits after line 1's row.
Runs 2 and 3 sent the recorded map. Run 1 also contested line 3. All
three wrote the line numbers as quoted strings (observed: the runs).

**What the probes say.** A written-out call and a guess row do not move
line 2 (observed: 0 of 6). The seat's fault of line 2 does not come from
the head or from `line_rows` (reasoned: the probes beside answer 2).

## 4. The placement, by `plans/wall-guide.md` section 4 in order

1. **An open frame's sign?** Yes, frame 305 holds the sign. The step
   adds the case to frame 305 and names no cause, so the order goes on
   (reasoned: section 4, step 1).
2. **The instrument?** The control map differs from the record on lines 1, 3
   and 6 to 8. Line 2 is contest in the record and in 7 of 7 calls
   here. The instrument does not make the sign (observed: section 3).
3. **His words or his page?** m90 reached the seat word for word as
   `principal_said` and `landing.reply`. The page is his page. No hop
   changed them (observed: s209 turn 1). Not cause 1 or 11.
4. **A door?** The door was right to fire, because m90 does not fault the
   guess line (observed: the provenance, section 4). Its step, "Approve
   2", is right, and the seat did not take it. Not cause 8 or 9
   (reasoned: cause 9 needs a wrong step that the seat follows).
5. **The rule's rows?** The door read m90 against the guess row and
   refused for the right reason. Not cause 6, 12, 14 or 15 (reasoned:
   step 4).
6. **The fact in the prompt?** The refusal is present and the reply holds
   a call (observed: s209 turn 1). Step 6 does not place it on the
   refusal.
7. **Present and read?** The seat read "Approve 2" as line 2 and judged
   against it (observed: answer 1). Cause 5's confirm first rules out
   causes 2 to 4. The fact the seat lacked is that m62 answered page m61,
   where line 2 is `cr_1`. No entry of `recent_chat` holds that fact, and
   `messages.cause_id` does (observed: section 1). **Cause 2: the prompt
   lacks the fact** (reasoned: cause 2's confirm, the fact searched in
   the prompt and absent).

This moves the read's W4 placement from cause 5 or 9 to cause 2
(reasoned: `plans/night158-read.md` W4 against answer 2).

## 5. The fix the answers point to, and its price

In `_recent_chat` (`rota/core/runner.py` 2445), each earlier reply of the
principal names the page it answered, and its "line N" turns into the row
id of that page's line N. A reply to the present page keeps its numbers,
so a stale line number can no longer name a row of the present page.

The price is 2 cycles, cause 2's cheap fix in the wake builder (observed:
`plans/wall-guide.md` cause 2). The measure is s209 turn 1 and s208 turn
1 replayed with the new `recent_chat`, 3 runs each, line 2 approved
(reasoned). The fix adds no sentence that tells the seat what to do, the
overfit cause 2 names (observed: the same).

## 6. What I doubt

- No probe here changed `recent_chat`. The fix rests on answer 2 and on
  the record, not on a measured move (observed: sections 2 and 3).
- At temperature 0 the three interview runs are one sample three times
  (observed: identical answers and token counts).
- m51 also says "Line 2 is wrong" about the guess line of page m50, and
  that fault is true of m50's line 2 (observed: `messages` m51). A row-id
  rewrite turns it into a fault of the guess row, which this page also
  shows as line 2. So the fix must name the page as well as the row
  (reasoned: m51 against m89).
- The control did not repeat the recorded map on lines 1, 3 and 6 to 8. The
  replay is near the night, not exact (observed: section 3).
