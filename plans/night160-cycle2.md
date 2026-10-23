# Night 160, cycle 2: bg_1 at review, three Critics on a line they cannot quote

This cycle belongs to frame 201, by the second half of its heading: frame 170's lines check loops the Critic to no verdict. The mechanism is the fragment key, the case that the stack's sprint list gives to frame 266 (W3 of night 158, `plans/stack.md` line 112). Frame 201's pass 3 hold fired 0 times, because the lines door refused every pass before the hold. Read-only read of `D:/repos/rota/.rota/clickI.db` (opened `?mode=ro`) and `D:/repos/rota/.rota/night160.log` to line 63. Night code `C:/Users/roman/rota_night160` at 695e8be7, which holds frame 201 pass 3d (8b1566c8 is an ancestor).

## Result

The three rounds are s148, s149 and s150. All three are Critic sessions on qwen3.5:9b, woken on `tick:review`, detail empty, refs `["bg_1"]`. None landed a verdict. The `tick_attempts` row `critic|tick:review|bg_1` is quarantined at attempts 3. The Liaison s151 woke on `tick:quarantined`, "1 abandoned: review for bg_1 (critic), 3 attempts", and sent page m45.

- The added line every Critic chose is `file.write(json.dumps(obj, separators=(',', ':')))`. The line holds single quotes. The seat wraps it in single quotes in `lines={...}`. Python then reads the dict as two keys: `echo_json_helper` with the value up to `separators=(`, and a phantom key `', '`. Section Probes shows the parse.
- The door answers "', ' is not a criterion of batch bg_1 ... Send the pass again with lines= naming each of them once" (`rota/roles/api.py:12412`). The text names the phantom key and not the quote. The seat cannot find its fault from it, and sends the same call again.
- When the seat changes the quotes, it drops the comma, `('', ':')`, and one closing bracket. The door then says "is not an added line" and offers the right line. No seat copied it. Cycle 1's Developer lost the same `','` in every `code.write`. The token run `(',', ':')` defeats qwen3.5:9b twice in one walk.
- The Critics did not judge wrongly. They tried to pass a diff whose test passes and whose output is what the principal asked for. No verdict landed, so frame 201's judgement sign did not fire.

What ended walk 1: the review tick of bg_1 was quarantined after s150, and the walk went quiet, "quiet after 64 steps, 6 asks", with "Stuck. The team gave up on: review for bg_1" (log lines 54 to 58, about 20:36).

## The sessions

| Session | Role, model | Wake | Tool calls | Writes | End |
|---|---|---|---|---|---|
| s143 | terminologist, qwen3.5:9b | m42 relay of m40 | 8 loads, `criteria.respecify` refused at seq 9, `msg.answer_tester` m43 OK at seq 10 | none, criterion stays v4 | before the cycle |
| s144 | tester, qwen3.5:9b | m43 answer | 5 loads, 4 `tests.encode` | tests tst_echo_json_02 v3 | before the cycle |
| s145 | critic, qwen3.5:9b | tick:review, ["bg_1"] | 3 loads, claim_encodes True OK, 10 `verdicts.emit` pass refused | none | attempt 1, refused to the end at turn 12 |
| s146 | critic, qwen3.5:9b | the same | 3 loads, claim True OK, 2 pass refused, 3 claim False refused, 4 challenge (seq 9 OK, m44), 2 fail refused | message m44 | attempt 2, ended after the challenge |
| s147 | tester, qwen3.5:9b | m44 challenge | 3 loads, 2 `tests.encode`, the second OK | tests tst_echo_json_02 v4 | between the rounds, resets the count |
| s148 | critic, qwen3.5:9b | tick:review, ["bg_1"] | 3 loads, claim True OK, 3 pass refused | none | round 1, "repeated its previous turn verbatim twice; ended" |
| s149 | critic, qwen3.5:9b | the same | 3 loads, claim True OK, 5 pass refused | none | round 2, refused to the end |
| s150 | critic, qwen3.5:9b | the same | 3 loads, claim True OK, 5 pass refused | none | round 3, "verdicts.emit was refused the same way in four turns" |
| s151 | liaison, qwen3:8b | tick:quarantined, ["bg_1"] | page m45 | message | after the cycle |

The three loads at seq 1 to 3 are `code.read`, `criteria.load`, `tests.load` in every Critic session.

What the Critic was asked to review, in every round:

- The diff of bg_1 at head 8877b1b8: `echo_json` added to `src/click/utils.py` after line 688. It writes the compact JSON, then writes a newline, then flushes.
- The criterion `echo_json_helper` version 4: "The function `echo_json` must not print any additional text (such as labels or prompts) before or after the JSON output." No later version exists, because s136 and s143 both had `criteria.respecify` refused.
- The test `tst_echo_json_02`. s145 and s146 saw v3 by s144, which asserts the stripped output equals the JSON and the output ends with a newline. s148 to s150 saw v4 by s147, which asserts the output equals the JSON plus one newline. Both pass at the head (log lines 49 and 50, "35 test(s), 0 not passing").

## Round 1: s148

- Turn 1: `verdicts.claim_encodes(echo_json_helper, True)` OK. `verdicts.emit(pass)` with `lines=` holding five added lines in one single-quoted string, the `(',', ':')` line among them.
- Turns 2 to 4: the door says "', ' is not a criterion of batch bg_1" three times. Turn 3 adds the NOTE "has been refused the same way in two turns".
- Account: three equal refusals and "repeated its previous turn verbatim twice; ended". No verdict.

## Round 2: s149

- Seq 5: the line `import json`. Door: "is a plain import ... The added lines of code are ..." with the five code lines.
- Seq 6 to 9: the json.dumps line with `('', ':')`, the comma lost and one closing bracket short. Door, four times: "is not an added line of the diff ... The added line nearest to it" with the right line. The NOTE fired at turn 4.
- The seat did not copy the offered line. No verdict.

## Round 3: s150

- Seq 5 to 8: the json.dumps line in single quotes, one closing bracket short. Door: the phantom key `', '` each time, and once "is not an added line".
- Turn 6: a dict that does not parse. Door: "could not parse arguments: ':' expected after dictionary key".
- Account ends "verdicts.emit was refused the same way in four turns; the session ended on it". No verdict.

## Before the rounds: s145 and s146

- s145 is the same loop as s150: three phantom-key refusals, then "is not an added line" five times, then one dict that does not parse. Its line never holds the diff's own text.
- s146 tried `import json` and the docstring line, both refused as lines that do nothing. Then it reasoned that no line "asserts" a negative criterion, and tried `claim_encodes(False)`. The door refused a second claim. It sent `msg.challenge_tester` m44, OK at seq 9, quoting the criterion and the v3 assertion. Its later fail was refused: "you have already challenged the tester this session".
- s147 answered m44 with test v4 (receipt `tests` v4). The test move ran `_forget_batch_counts` (`rota/core/db.py:650`), so the review count restarted at 1 for s148.

## Why no verdict landed

1. The cause is a door refusal that names the wrong thing, in a loop on the lines check. The seat's dict splits on its own quotes, and the door names the fragment key `', '`. Frame 170's lines check loops to no verdict: this sign fired in all three rounds and in s145.
2. The second cause is the seat's copy. The seat cannot reproduce `(',', ':')` with the right quotes, comma and brackets. The door offered the exact line as "nearest" in s145, s149 and s150. No seat sent it.
3. Frame 201's judgement sign did not fire. No pass landed. The lines the seats chose do what the principal asked, and the criterion's examples, labels and prompts, do not exclude a newline.
4. Frame 201 pass 3's hold fired 0 times. The hold runs after the lines check, and no pass reached it. Night 158 masked it the same way (stack, frame 201 status 2026-10-21 16:23).
5. The prompt is one the seat can act on. The diff, the criterion and a passing test are all in turn 1.

## The quarantine and what put the Critic there

The Critic did not review a quarantined batch. Cycle 1's row `developer|tick:tests_failing|bg_1` is gone from `tick_attempts`. `_lift_quarantines` (`rota/core/db.py:647`) deleted it when s144 moved a test of bg_1 (receipt `tests` tst_echo_json_02 v3). The chain to that move starts at the ruling m40, not at the runner's own tick:

1. m39 re-presented the page. He answered m40, "Line 3's check is still wrong".
2. m40 was recorded as the verdict m41. The Liaison s142 woke on m41 and sent the relay m42 to the Terminologist s143.
3. s143's `criteria.respecify` was refused, because the surface `tests/test_echo_json.py::test_echo_json_output_format` "is not a symbol the index knows". s143 then sent `msg.answer_tester` m43 with the criterion still at v4.
4. s144 encoded v3 on m43. The harness then read 0 not passing, and `tick:review` woke the Critic.

So the review wake is the runner's tick, and the ruling m40 opened it. The new quarantined row is `critic|tick:review|bg_1`, attempts 3, quarantined 1, reported 1.

## The frame

Frame 201. The sign is its heading's second half, "frame 170's lines check loops the second to no verdict", in s148, s149, s150 and s145.

- 201: yes, by the lines check loop. The fragment key is the mechanism, which the stack assigns to frame 266 as night 158's W3 case. Frame 201's own hold never ran, so this night cannot validate pass 3.
- 310: no. The criterion v4 is the one the Critic read, and no `criteria.specify` ran in the cycle.
- 308: not in the cycle. s143 before the cycle is 308's sign again: an answer after a refused respecify, as s136 was in cycle 1.
- 306: not in the cycle. His words reach the test v4 through the test route, while the criterion keeps v4.

## Findings

1. `rota/roles/api.py:12410` to `12414`, high, CONFIRMED. The phantom-key refusal names `', '` and not the quote that split the value. The probe parses the s148 and s150 calls into two keys. Fix: when a key is not a criterion and a criterion key is also present, say that a quote inside the line closed the string, and offer the line in double quotes.
2. The not-an-added-line refusal in `verdicts.emit`, low, CONFIRMED. The door offered the right line in three sessions, and no seat copied it. The token run `(',', ':')` is the wall, as in cycle 1. Fix: accept the offered nearest line by a number or a key, so the seat need not copy quotes.
3. Outside the points, low, CONFIRMED: page m45 says "The team stopped work on this change", and m46 asks "What did the review object to". The review never landed and never objected. Fix: the quarantine page names a review with no verdict as a review that did not finish.

## Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad/c2_p1.py` to `c2_p7.py`: read-only queries on sessions, tick_attempts, tool_calls, turns, receipts, criteria, tests and messages.
- An inline `python -c` read the first `verdicts.emit` of s148 and s150 and ran `ast.literal_eval` on the `lines=` value. The result was a dict of two keys, `echo_json_helper` and `', '`.
- An inline `python -c` printed the test row in turn 1 of s145, s148, s149 and s150: v3 for s145, v4 for the rest.

## Usage

About 90k input tokens and about 12k output tokens on the harness line, about 102k in all, against the 60k cap.
