# Frame 335, the agency read

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`, read only. The frame's fix is built at 71642373, 3954f537, 9a22a120 and 0fcbce6d above 3bb5be4b. No pytest ran. Night 168 was read from a backup copy in the reader's scratch folder.

## The result

**At one door of 10: the fix covers 4 of 10 instances.** The frame's own provenance names the view as the cause of the quote face, and the fix reads the view's escape level back at the quote door. The view, the code door and the three call-form refusals keep the gap (reasoned: sections 3 and 4).

## 1. The purpose

- The parse check of `tests_encode` (`rota/roles/api.py` 9223, the parse at 9328) came in bfd149d1, 2026-09-01 20:14, "a test is Python the harness can run". It closed S0's stall, where a Tester encoded an English sentence and the fix loop had nothing to fix. Its body says "ast.parse has no opinion about quality, only about whether anything can execute" (observed: the commit body). It is a build decision. No ruling made it (observed: `plans/c2-escape-provenance.md` section 6).
- `_note_collection_error` (api.py 17606) came in 5ae7f5f5, 2026-10-26 07:51, frame 328 pass 4. It tells the Tester that a stored body errors at collection (observed: the commit subject).
- The challenge door `_challenge_evidence` came in 395535da, 2026-08-27, and `_cites` with its floor in a9231619, 2026-10-26 01:40, frame 328. The door makes a Developer's challenge carry a verbatim span of each disputed row (observed: the commit body of a9231619).
- None of the three mechanisms was designed for an escape level. No ruling names the escape level of a call value (observed: the provenance, section 6).

## 2. What exists

| What | Where | What it does for this frame's fault |
|---|---|---|
| `_as_block` | `rota/core/runner.py` 1867 to 1901, b8c18fec, 2026-08-24 | Shows a result's long text plainly, because a JSON string showed "every newline `\n` ... every quote `\"`" (observed: its docstring). It takes a flat dict of strings only |
| `_as_table` | runner.py 1836 to 1864 | Shows a list of same-key rows with each string as written. `criteria.load` reached s147 this way, with one backslash (observed: night 168 s147 seq 2, offset 4262) |
| `_render` | runner.py 1904 to 1910 | Falls through to `json.dumps` for any other shape. `tests.load` is a dict of lists, so its bodies reached s147 at the JSON level, `\"AppData\\\\Roaming\"` (observed: s147 seq 2, offset 6405) |
| `_span_of` decode | `rota/core/sandbox.py` 1270 to 1271 | Reads the JSON forms `\n`, `\t`, `\"`, `\'` of a quote back. Night 124 (observed: its docstring) |
| `_quoted_body_gone` | sandbox.py 2388 to 2389, deeda588, 2026-10-12 | Undoes the JSON escapes of a prompt, `\\` included. Night 142 (observed: its comment) |
| `_seat_forms`, `_unescaped` | sandbox.py 1288, 1339 | Read `\'` and a control escape back, frame 328 (observed) |
| `_one_backslash` | sandbox.py 1325, frame 335 | Reads `\\` back, both halves of `_cites` (observed: 3954f537, 9a22a120) |
| `_call_keeps`, `_raw_advice` | api.py 17530, 17554, frame 335 | Probe a form through both parse paths of the call (observed: 9a22a120) |
| `_repair_broken_strings` | api.py 22312, night 99 | Joins a line break that the call decoder put inside a string of `code.write`. The same level, `\n` only (observed: its docstring) |
| `-W ignore::DeprecationWarning` | `rota/core/harness.py` 237 to 241, night 55 | Relaxes the project's warning filter for the Tester's own tests. SyntaxWarning stays an error (observed) |

## 3. The reach

The cause by the code has three parts. A door parses seat Python under a rule that is not the project's collection rule. The call's escape level is the default of the parse path, and no text names it. The result view shows a test body at the JSON level, one level above the row (observed: provenance sections 1 to 3, "The cause of the four backslashes is the view").

| # | Instance | Where | Fix covers |
|---|---|---|---|
| I1 | The encode parse admits an invalid escape | api.py 9328 | yes |
| I2 | The collection note copies pytest's level | api.py 17606 | yes |
| I3 | The code door parses with no warning filter and compiles with warnings off. A Developer's `"C:\Roaming"` in a module lands, and the project's collection fails when a test imports it | api.py 19229 to 19245, f414b18f, 2026-09-30 | no |
| I4 | A call-form refusal says "Write the value as it is, with no backslashes" | `rota/llm/toolproto.py` 1440 to 1447 | no |
| I5 | The same, "{write}, with no backslashes" and "No escaping" | toolproto.py 1524 to 1534 | no |
| I6 | The same, "write every line of the value as it is ... No escaping" | toolproto.py 1537 to 1544 | no |
| I7 | Two parse paths, two levels, no mark of the path: strict `literal_eval`, fallback raw text for a quoted value and decoded text for an unquoted one | toolproto.py 818 to 836, `rota/llm/_lenient.py` 77 and 90 | no, probed around by `_call_keeps` |
| I8 | The view: `tests.load` falls through to `json.dumps` | runner.py 1910 | no |
| I9 | The test half of `_cites` compares the view's level | sandbox.py 1659 to 1673 | yes |
| I10 | The criterion half of `_cites` | sandbox.py 1666 to 1671 | yes |

Count: 10 (observed: the lines; reasoned: I3's collection failure follows from clickI's `filterwarnings = ["error"]` and pytest's collection filter, not run). The older decodes in `_span_of` and `_quoted_body_gone` are not counted. They show the pattern: four door-local decodes of one view since night 124, one escape each (reasoned: section 2). The `_quotes_span` doors at sandbox.py 983, 1216, 1222 and 1710 read the same view through a 12-character window and tolerate it, so they are not counted (reasoned: a window without a backslash matches).

## 4. The fix against the reach

- The built fix covers I1, I2, I9 and I10, 4 of 10 (observed: the diff 3bb5be4b..0fcbce6d touches `api.py` 9319 to 9341 and 17491 to 17598, and `sandbox.py` 1325 to 1330, 1420 to 1428 and 1654 to 1673 only).
- It leaves I3: the code door and the test door now read the same SyntaxWarning by two opposite rules (observed: api.py 9327 `"error"`, 19242 `"ignore"`).
- It leaves I4 to I6: the refusals that teach the call form still say "as it is" and "no backslashes", and the strict path decodes a backslash in that form (reasoned: provenance section 4).
- It leaves I8, the cause the provenance named for W2. `_one_backslash` reads one escape of the view back at one door, the fifth door-local decode of that view (reasoned: section 2).
- It leaves I7 by design. The frame records the fallback faults for a later read (observed: status 18:59).

## 5. The proposal

Not the same fix. The encode refusal and the note stand. The rest moves to the two sources:

1. Show nested text plainly in `_render` (runner.py 1904), as `_as_block` (1867, 2026-08-24) does for a flat dict, so `tests.load` shows one backslash (s147 seq 2, 6405). `_one_backslash` (sandbox.py 1325) then goes.
2. Move `_call_keeps` and `_raw_advice` (api.py 17530, 17554) beside `parse_args` (toolproto.py 791), as the one statement of the call's level.
3. Give I4 to I6 (toolproto.py 1440, 1524, 1537) that statement when the value holds a backslash, in place of "no backslashes".
4. Give `code.write` (api.py 19232) the same SyntaxWarning parse and `_escape_refusal` (17595). Keep compile's other warnings off, frame 94's reason (f414b18f).
5. Leave I7 to its own read, as the frame's status of 18:59 and review 1 findings 6 and 7 (`plans/frame335-review-p1.md`) record.

Price: about 3 cycles, one implementer pass and one review, a door text and an instrument (reasoned: `plans/operating-facts.md` 247). Agent tokens about 75k for the pass and 65k for the review (reasoned: the same page, 244 and 243). About 30k of the holding session's context at 10k a cycle (reasoned: 247). Step 1 changes every recorded prompt that holds `tests.load`, so stale replay cases add a pass (reasoned: not counted).

## 6. The doubt

- I3 is reasoned: no night read was searched for a Developer `code.write` with an invalid escape, and no probe ran pytest on such a module.
- Step 1 is reasoned from one prompt, s147. Other shapes that fall to `json.dumps` with code text were not listed, and the cassette count for step 1 is unknown.
- Whether the gate's five known reds hide the two stale cases of review 1 point 7 was not checked.

## Verdict

`at one door of 10`: the fix covers 4 of 10 instances. Not covered: I3 the code door, I4 to I6 the three call-form refusals, I7 the two parse paths, and I8 the `json.dumps` view of `tests.load`, the cause the provenance itself names for the quote face.
