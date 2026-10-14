# Frame 202, pass 1: the diff review of the respecify door (ee535945)

Verdict: revise. Two high findings block the accept. The next pass's brief is findings 1 to 3.

## (a) The verdict on each point

1. Agree on every row my script saw. My script did not see s248, s310 and s135, so it neither confirms nor contradicts those rows.
2. A right move is refused. The text rule refuses a restore when the text names the wrong callable as a helper.
3. A right move is refused. The comparison rule refuses "I would like echo to take a json flag", and the principal asks for echo itself.
4. The text-rule refusal has two routes. The comparison refusal has one route, and that route fails when the principal asks for the new callable.
5. On a tick:criterion_repair wake with no ruling, the words list is empty. The comparison rule then never fires, and the text rule runs alone.
6. Three tests are red on the parent, as the implementer says. Four branches have no test.

## Point paragraphs

Point 1. My script (p_count.py) parses the respecify calls itself and calls _surface_move_fault with the words of the newest non-stale ruling written before the session. It refuses s591 on night 144 and both s160 moves on night 146. It does not refuse s291, s304, s272 or s292. These results agree with measure.out. My surface tracker only learns a surface from a paired OK result in the same night. So it did not see the moves of s248, s310, s135, s190, s261, s321, s340 and s609. My pairing marks both s304 calls ERR, and the implementer marks t2 as moved. Neither difference changes a count of refusals. Outside the brief's table, measure.out shows two unrefused wrong moves: night 144 s190 cj_serializable echo_json to echo, and night 145 s261 version_option to custom_version_option. The second is the reverse of the s272 to s340 repairs, which the brief calls right.

Point 2. The text rule reads every backticked span of the criterion text. Then it keeps only the old surface's symbols, the item id and the item's backticked callables in a callable form. That matches the brief's limit. The old-surface clause is the defect. A criterion that names the old callable as a helper or as a second callable is refused on a right move. Probe case A: the text says "`echo_json` ... writes the string through `echo`", the surface is echo, and the move goes to echo_json. The door refuses and says "Keep `utils::echo`", which is the wrong callable. Probe case B: "`parse_version` returns a tuple that `version_option` prints" refuses a move from version_option to parse_version.

Point 3. The cue rule matches "like {n}" anywhere in the words. Probe case D: "Drop echo_json. I would like echo to take a json flag instead." The door refuses the move to echo and calls echo a comparison. Probe case E: "Put the flag on echo itself, and have it handle the newline the way echo does today." The door refuses that move too. The "at least once" choice of the implementer makes case E reachable. One cue anywhere in the newest ruling on the criterion or the item outweighs a plain request.

Point 4. Both texts are STE. Both name the callables and the action. Neither uses a pronoun for the principal. The text-rule refusal routes to "Keep" or "rewrite the text". In case A the "Keep" route names the wrong callable, and the "rewrite" route names text the criterion already holds. The comparison refusal routes to "Keep the surface" only. When the principal asked for the new callable, the seat has no route, and every retry meets the same words. That is the frame 197 loop. Neither refusal uses _offer, so the seat gets no ready call.

Point 5. The call site reads last_ruling_on for the criterion and for the item, and the trigger's messages.body_text when the verb is relay. On a tick wake the trigger is no relay, so only the rulings add words. With no ruling on file the list is empty, and _surface_move_fault skips the comparison rule. The relay route reads a column that no relay of nights 144 to 146 fills. The seat reads principal_said from entry_for on the cause chain (rota/core/runner.py:1696 and 1765). So the door and the seat can read different words.

Point 6. On a git archive of bf3ae643 with the new test file, three tests fail: test_a_text_that_names_the_old_callable_keeps_its_surface, test_a_callable_named_as_a_comparison_is_not_the_surface and test_a_relay_that_names_a_comparison_is_read. Three pass. These branches have no test: the "Name `<name>` in surface_refs" refusal, the called=True filter of the item text, the comparison rule's guard when the old surface is not a carried name, and a restore whose text names the wrong callable.

## (b) Findings

1. rota/roles/api.py:4870-4878, high, CONFIRMED. The text rule refuses a restore to the item's callable when the text names the wrong callable in backticks. Probe case A refused it and told the seat to keep `utils::echo`. Fix: skip the text rule when a new surface symbol is the item id or a carried callable.
2. rota/roles/api.py:4885-4900 and 4815-4817, high, CONFIRMED. The comparison rule refuses a move that the principal asks for, and the refusal gives no other route. Probe cases D ("I would like echo") and E ("echo itself ... the way echo does") refused. Fix: drop the bare "like {n}" cue, skip the rule when the words name the new callable without a cue, and add a route "or rewrite the text if the principal asked for `<new>` itself".
3. rota/roles/api.py:4870-4878, low, CONFIRMED. The text rule refuses a move away from a second callable the criterion names. Probe case B refused version_option to parse_version. Fix: fire only for the first backticked callable of the text, or only when no new symbol is in the text.
4. rota/roles/api.py:4980-4984, low, CONFIRMED. The relay route reads messages.body_text, which no relay of nights 144 to 146 holds, and the seat reads principal_said from entry_for. Fix: read entry_for on the trigger and on chain_verdict's cause, as the runner does.
5. tests/rota/test_frame202_surface_move.py, low, CONFIRMED. Four branches have no test, and the relay test builds a row the night never writes. Fix: add a test for each finding above and for the "Name in surface_refs" branch.
6. Outside the points. measure.out, night 144 s190 and night 145 s261, low, CONFIRMED. Two wrong moves pass the door, beside s135. Fix: count them in the residue of the s135 rule, in pass 2 or a new frame.

## (c) Probes

All under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv202/.

- p_rules.py: calls _surface_move_fault on seven constructed shapes, A to G. A, B, D and E refuse right moves. G (s135's shape) returns None.
- p_count.py: an independent parse of nights 144 to 146 (mode=ro). It calls the door on each move it can pair.
- parent/: git archive of bf3ae643 with the new test file. pytest on the file: 3 failed, 3 passed.

## (d) Usage

From the context counter: about 58k in, about 6k out, about 64k total. The 50k cap was passed by about 14k, mostly on the system context.
