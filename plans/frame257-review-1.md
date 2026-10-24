# Frame 257, review 1: passes 1 and 1b at 51b29993

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r308` at 51b29993, 2026-10-24. Night databases and `tests/rota/cassettes.db` were opened with `?mode=ro`. No gate, no re-record, no suite run.

## (a) Verdict

51b29993 goes on the branch after the gate. The door does what option A says, and no qwen3:8b recording writes one id twice with other words. The findings are low. One finding corrects the pass report's explanation of the 6 same-text repeats.

1. Door against option A: PASS. The refusal names the fact, quotes ten words, offers `criteria.specify` with `INVENT` through `_offer`, and names `msg.challenge_vision_keeper` for a landed row. `criteria.tools` lists both routes. The same text twice meets the twin refusal of 6413e4ee, byte for byte.
2. The count: the replay is right and the pass's explanation is wrong. The nights refused all 6 same-text repeats with the twin refusal. The "OK" labels come from the transcript parser. The 54 comes from the same parser. A full-session replay at the old door admits 52 of the 54.
3. Recorded cases: no case goes red. Four qwen3:8b cases call `criteria.specify`, and 0 of their 10491 runs write one id with two texts. The brief edit makes their `tick:criteria` recordings STALE.
4. Brief sentence: PASS. The sentence is short and the seat can act on it. No other brief calls `criteria.specify`.
5. Red tests: PASS. Both nights' seq 7 and 8 arguments match the test constants exactly, after the night's own parser.

## (b) Point 1: the door

- api.py 5299 to 5322 runs only when `prior_ticket == ticket_id`. The prior text is the last staged write of the id, or the landed row.
- Probe s13 sent three second texts under one id. Other words: refused with "'c_a' already holds a criterion on tk_1: '...'. An id you invent is yours once. For a new criterion, send criteria.specify with a new id of your own." Case change only: the twin refusal. Punctuation change only: the near-duplicate refusal.
- `rota/roles/prompts/terminologist/criteria.tools` lists `criteria.specify` (line 1) and `msg.challenge_vision_keeper` (line 7). The refusal never names `criteria.respecify`.
- The twin block at api.py 5329 to 5346 is not in the diff. `test_the_same_text_twice_keeps_the_twin_refusal` anchors the full text at both ends.

## (c) Point 2: the count

- Probe s3 found the 6 repeats: night 140 s312 (3), night 141 s139 (1), night 142 s512 (2).
- Probe s4 printed their transcripts. Each repeat got "ERROR criteria.specify: those are <id>'s words already, on the same ticket". Night 140 s312 then got the frame 144 note "refused the same way in three turns".
- The cause is the parser in `scratchpad/f257/count.py`, `session_calls`. The last turn's user text replays earlier results out of order. The parser pairs each OK or ERROR with the first pending call of that name. A re-rendered OK line pairs with a later call.
- The night door and the replay door agree. The pass's "likely older code" reason is false. The twin check dates from 395535da, 2026-08-27.
- Probe s5 replays every parsed call of each session, in order, with every item and ticket of the night. At the old door, 52 of the 54 night-OK other-word repeats pass, and 2 meet another door. At the new door, 53 are refused. Night label and replay disagree on 62 of 558 calls, so the replay is an estimate.
- The real count is between 52 and 54. The parser can mislabel, so 54 is an upper bound.

## (d) Point 3: the recorded cases

- No case YAML names `criteria.specify`. The calls live in the cassette database, `tests/rota/cassettes.db`.
- Probe s11 parsed 48595 calls in 12121 case runs. Four cases run on qwen3:8b: `L1-TE-specify-criteria` (2949 runs), `L1-TE-a-new-behaviour-is-a-new-callable` (2979), `L3-scope-becomes-a-ticket-with-criteria` (2325), `L3-a-challenge-reaches-the-role-that-can-answer-it` (2238).
- 0 qwen3:8b runs write one id on one ticket with two texts. So the door turns no qwen3:8b case red.
- llama3.1:8b (115 runs) and qwen3:4b (10 runs) of two L1-TE cases do write one id twice. The gate runs qwen3:8b only (gate.py 47), so these runs do not count.
- The criteria brief changed, so the four cases go STALE. Their re-record meets the new door live. That flow is not measured.
- The python tests that call the door use distinct ids. `rota/testkit/scenes.py` 499 uses `c{n}`. The pass ran 15 files green.

## (e) Point 4: the brief sentence

- `criteria.md` 37 to 38: "Each criterion has its own id, and a new text takes a new id." It states both rules in one plain sentence. It sits after the "six is many" paragraph, where a seat plans its criteria.
- Only `terminologist/criteria.md` and `criteria.tools` name `criteria.specify`. No other brief needs the sentence.

## (f) Point 5: the red tests

- Probe s12 parsed the first two `criteria.specify` lines of s111 and s114 with `rota.llm.toolproto.parse_args`. Both are seq 7 and 8.
- `_FIRST`, `_SECOND`, the term refs stream and line, and the surface ref echo_json match exactly. The parsed `_SECOND` holds a newline character, and so does the test constant.
- The item text and the `tk_1` text in both databases equal `_ITEM`. Nights 149 and 160 hold the same calls.

## (g) Findings

1. Pass report, Pass 1b, line 64. Low. CONFIRMED by probe s4: the nights refused the 6 same-text repeats with the twin refusal, and the "OK" labels are parser errors. Fix: correct the line in the frame's record, and name the parser as the cause.
2. `scratchpad/f257/count.py`, `session_calls`. Low. PLAUSIBLE: the same pairing error can label a refused call OK. Probe s5 admits 52 of 54 at the old door. Fix: write the count as "52 to 54" where the frame cites it.
3. `tests/rota/test_criteria_one_id.py` 61. Low. CONFIRMED by reading: the `night` parameter is unused, so both cases run the same calls. Fix: keep one case and name night 149 in the comment, or accept the duplicate as a label.
4. Outside. `rota/core/identity.py` 51. Low. PLAUSIBLE: the criteria entry of `NATURAL_KEYS` says "same ticket, same words, one row", and not that one id holds one text. Fix: add "one id holds one text on its ticket" to the description.
5. Outside. api.py, the `criteria_respecify` docstring and the "No reader reads a criterion's version" comment. Low. CONFIRMED by the diff: provenance findings 2 and 3 are not in 51b29993. Fix: carry them to the next pass, or close them in the stack.
6. Outside. api.py, the near-duplicate block. Low. CONFIRMED by probe s13: a punctuation-only rewrite under one id gets "this says what c_a says", which names the seat's own id. The behaviour predates 51b29993. Fix: none in frame 257.

## (h) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/r257/`.

- s1.py: the `tool_calls` schema and the rows of night 160 s111.
- s2.py: the `criteria.specify` calls and results of s111, from the last turn.
- s3.py: the pass parser, and the groups with same-text OK repeats over nights 140 to 159.
- s4.py: the transcripts of the 6 repeats.
- s5.py: a full-session replay of every parsed call, at the new door and with the new block disabled (argument `old`).
- s6.py and s7.py: the cassette database schema.
- s8.py, s9.py and s11.py: a scan of `case_runs` transcripts and `cassettes` completions for one id with two texts. s11.py is the working version.
- s10.py: the format of one transcript.
- s12.py: the night arguments against the test constants.
- s13.py: the door on other words, on a case change and on a punctuation change.

## (i) Usage

The exact counts are not visible to the reviewer. Estimate: about 60k input tokens, 14k output tokens, 74k total. The review went over the 25k cap, mostly on the cassette scan and the night transcripts.
