# Night 159, cycle 1: page m116 and its re-present

Read-only read of `D:/repos/rota/.rota/clickI.db` (mtime 16:28, opened with `?mode=ro`) and `D:/repos/rota/.rota/night159.log`. Night code at 73a4801f. The frame 283 removal commits (a7012122 to a4645b0d) are not in the night's code.

## Result

The three rounds are s239, s240 and s241. All three are Liaison sessions on qwen3:8b with wake `message|converse`, and none landed a ruling.

- s239 and s240 answer m117. They contest line 2. The words do not fault line 2. The door refuses with a right text, and the seat repeats the call. The line numbers come from an earlier reply in `recent_chat`. That is frame 272's sign.
- s241 answers m118. The seat contests line 1. The door refuses it, right on line 1. But the door says the words fault lines 6 and 8 only, and it tells the seat to "approve the rest". The words also fault lines 3, 4, 7 and 14. The line reader misses "delete line 7", "delete line 14" and "In lines 3 and 4, replace ...". That is a wrong line-reader refusal. Its cause is not in frame 305's texts or in frame 272's.

## The sessions

| Session | Woken on | Rounds | Model |
|---|---|---|---|
| s238 | m115 (submit) | before the cycle | qwen3:8b. It called `ledger.list`, then `msg.present_principal(refs=[bg_2_summary, confirm_default_on_eof, ..., echo_json, ...])`. This sent page m116. |
| s239 | m117 (converse) | round 1 | qwen3:8b |
| s240 | m117 (converse), prompt "A session on this reply ended with no ruling. Its last refusal or error: rulings.rule: the words do not fault the code of confirm_default_on_eof. Approve 2." | round 2 | qwen3:8b |
| s241 | m118 (converse), the answer to the re-present | round 3 | qwen3:8b |
| s245 | m120 (converse), after the cycle | landed r_84b69b4f0d | qwen3:8b |

Page m116 lines (from the `landing.lines` of s241's prompt): 1 `confirm_default_on_eof` (request), 2 `guess:confirm_default_on_eof` (code row), 3 to 8 `cr_1` to `cr_6`, 9 `how_it_works`, 10 `bg_2_summary`, 11 to 13 description items, 14 `l_e6df5e65b3` (ledger note).

The messages: m117 "Line 7 should go, because confirm has no option or sentinel. Lines 3, 4 and 6 are off: ... The line 8 check needs prompt text like "Continue?" ... and I already answered line 14 earlier." m118 "Please delete line 7, ... and delete line 14, ... In lines 3 and 4, replace "raises a usage error" with "aborts", ... In lines 6 and 8, change the checks ...". The `messages` row of m116 keeps `unresolved_note` "m117: rulings.rule: the words do not fault the code of confirm_default_on_eof. Approve 2."

## Round 1: s239 (m117)

- Call, 3 rows in `tool_calls` and 6 tool turns: `rulings.rule(rulings={1: "contest", 2: "contest", 3..7: "contest", 8: "revise", 9: "approve", 10: "revise", 11..13: "approve", 14: "contest"}, words="Line 7 should go, ...")`. Turns 2, 4 and 5 wrote `14: "contest}` with no closing quote.
- Door: `rulings.rule: the words do not fault the code of confirm_default_on_eof. Approve 2.` (three times). The parser refused the malformed turns: `unterminated argument list: a string in the value of rulings starts at character 197 ... The string "contest} has no closing quote before , words= ...`.
- Turn 7 is prose with no tool call. Its reasons for lines 1, 2 and 3 copy the principal's m106 reply to page m105, "should cover only the confirm flag, not the JSON echo helper", "should specify that confirm gets a flag that is off by default", "should name the confirm function in Click's terminal prompt code, not the exceptions file". m106 sits in `recent_chat` with no page id.
- End: the session ended with no ruling. The runner's account lists the two refusal texts.

## Round 2: s240 (m117 again)

- Call, twice in `tool_calls`, three tool turns: `rulings.rule(rulings={"1": "contest", "2": "contest", ..., "7": "contest", "8": "revise"}, words="Line 7 should go, ...")`. Lines 9 to 14 are missing.
- Door: `rulings.rule: the words do not fault the code of confirm_default_on_eof. Approve 2.` (twice).
- End: `repeated its previous turn verbatim twice; ended`. No ruling. After this round the page was re-presented: "Your last answer to this page did not reach the team. The team could not turn your words into a ruling." The re-present names no line.

## Round 3: s241 (m118)

- Call, 4 rows in `tool_calls` and 6 tool turns: `rulings.rule(rulings={1:"contest", 2:"approve", 3:"contest", 4:"contest", 5:"approve", 6:"revise", 7:"contest", 8:"revise", 9..13:"approve", 14:"contest"}, words="Please delete line 7, ...")`. Turns 2, 4 and 7 wrote `14:"contest}` with no closing quote. Turn 6 called `rulings.line(1)` to `rulings.line(14)`, 14 calls.
- Door: `rulings.rule: The words fault lines 6 and 8. Line 1 is the request, and they do not fault it. Rule lines 6 and 8, and approve the rest.` (four times). The malformed turns got `unterminated argument list: ... character 183 ...`.
- Turn 6 prose shows the seat took the refusal as fact: "The principal's reply faults lines 6 and 8, but line 1 is the request and should not be faulted. I will rule lines 6 and 8, and approve the rest." It then sent the same call again, line 1 still contested.
- End: `rulings.rule was refused the same way in four turns; the session ended on it`. No ruling.

## Where the words stopped

In rounds 1 and 2 the words stopped at the guess door of `rulings.rule` (`rota/roles/api.py:10554`). The door refused the contest of line 2, the code row of `confirm_default_on_eof`. That refusal is right: neither m117 nor m118 names line 2. The seat's line-2 contest and its line-1 contest come from m106, the principal's reply to the earlier page m105, which `recent_chat` carries with its line numbers and no page. In round 3 the seat approved line 2 and the words stopped at the request door (`_request_refusal` text at `api.py:9852`). That refusal names lines 6 and 8, and the words do fault both, so the refusal names no line the words do not fault. But the refusal is incomplete, and its instruction is wrong. `_line_cues` on m118 returns `{6, 8}` only (re-run on the current tree, read-only), so "approve the rest" tells the seat to approve lines 3, 4, 7 and 14, which m118 asks to delete or replace. The same reader on m117 returns `{7}` only and misses "Lines 3, 4 and 6 are off", "The line 8 check needs" and "line 14". The seat's contest of line 1 was its own error, and the door was right to refuse line 1.

## Which frame

The cycle splits across two causes.

- s239 and s240 belong to frame 272. Frame 305's second ends-when counts "Liaison sessions that end on a repeated right refusal of a line-2 contest, from 2 cycles toward 0 of the next 3", so this cycle counts 1 against frame 305 on that line. But frame 305's status of 2026-10-23 14:08 already judged that sign "frame 272's residue": a `recent_chat` reply with line numbers and no page. Here the source is m106 (page m105), and s239's turn 7 copies its line 1, 2 and 3 reasons. That is frame 272's ends-when, third clause: a first session that contests a line from an earlier page's reply. Frame 272's fix (each earlier reply names its page, and its line numbers become that page's row ids) is unbuilt, so the sign is expected.
- s241 belongs to neither frame. Its refusal is a wrong line-reader refusal, which frame 305's second clause counts ("wrong line-reader refusals, from 1 toward 0"). But frame 305's mechanism is "drop it" after "line 7 repeats line 3", and the re-present text. The cause here is that the line reader has no cue for "delete line N" or for "In lines N and M, replace X with Y". So by frame 305's third clause ("the frame closes when its cause is not these texts") s241 is a new wall. The re-present names no line, so it does not break frame 305's re-present test. The removal commits of frame 283 are not in the night code, and they read removals in commits, not in line cues.

After the cycle, s245 landed r_84b69b4f0d on m120, the principal's third answer to m116: contest lines 3, 6, 7, 8 and 14, approve the rest. Line 4 was faulted in m118 and m117 but not in m120, so it was approved.

## bg_2 deferred: "its ladder is spent"

Log line 99: `do:park: deferred bg_2; its ladder is spent`. The batch reached attempt 11 against `loop_cap` 10 at head c29d89dd. Three tests failed there (`test_runs`, attempt 11: `tst_cr1_default_off`, `tst_cr4_plain_function_default`, `tst_cr6_simple_default_return`). Every rung of `LADDER = ("developer", "architect", "vision_keeper")` had a committed `tick:exhausted` session on bg_2: s185 developer "attempt 10 of 10", s189 architect "attempt 11 of 10", s194 vision_keeper "attempt 11 of 10". So `parked()` was true and `_next_rung()` returned nothing. The `preempt` predicate (`rota/core/predicates.py:1609`) then woke `do:park`, and `lifecycle.defer` set the row `('bg_2', 'confirm_default_on_eof', ...\worktrees\bg_2, 'c29d89dd...', 'deferred', 41000, 1)`.

## bg_3 abandoned: "its item is no longer schedulable"

Log line 102: `do:cancel: abandoned bg_3: its item is no longer schedulable`. The batch bg_3 was built for item `bg_2_summary` (formed after s219 grouping and s224 annotate). The principal's reply m106 to the touch page m105 said "Line 1 is wrong because this page should cover only the confirm flag". Ruling r_d6e3aa5128 landed `{"bg_2_summary": "contest", "cr_echo_json_prints_compact": "revise", "bg_3": "contest"}`. The contest of the item put its approval behind its version, and the `cancel` predicate (`predicates.py:1554`, `approval != 'approved' OR approval_ver < version`) woke `do:cancel`. Row: `('bg_3', 'bg_2_summary', None, None, 'abandoned', None, 1)`. The item is now `approved`, version 2, `approval_ver` 2, after r_193e4d9c9a on m112.
