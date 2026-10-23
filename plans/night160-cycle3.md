# Night 160, cycle 3: the Critic on bg_2

## Result

No, cycle 3 is not the same loop. The three rounds are s205, s206 and s207. All three are Critic sessions on qwen3.5:9b, woken on `tick:review`, refs `["bg_2"]`. No verdict landed in the cycle. The `tick_attempts` row `critic|tick:review|bg_2` is at attempts 3, quarantined 1, reported 1.

- The quote parse is not the fault. Every `lines=` value parses to the three criterion keys, `cr_1`, `cr_2` and `cr_3_confirm_default_on_eof` (`tool_calls` seq 7 of s205, s206, s207).
- The door that loops is the docstring refusal of `verdicts.emit`, `rota/roles/api.py:12554`. For `cr_3` every Critic quoted a docstring line, `':param default_on_eof: If True, when stdin is closed (EOF), return the'`. s205 first sent five docstring lines in one value.
- The refusal text: "is a docstring line, and a blank line, `pass`, `...`, a comment, a plain import or a docstring line does nothing that a criterion asks for. Copy the added line that does what cr_3_confirm_default_on_eof says". s205 got the five-line form: "holds 5 lines, and they are docstring lines".
- The door is wrong for this criterion. `cr_3` v7 by s195 reads "Line 4's check must verify that confirm()'s docstring explains the 'default_on_eof' flag". Only a docstring line can meet it. The door offers three code lines, and none of them explains the flag.
- The door also offers the fail route. No seat took it, because the seat judges the docstring as a pass. s188 before the cycle took that route once, and its fail verdict on `cr_3` at 6ed4f8b4 is the only verdict of bg_2 (`verdicts` row `critic:bg_2:6ed4f8b4...`).
- s198 and s200, the review rounds before the reset, got the same refusal 10 times between them and the challenge route. The loop is one door across six Critic sessions.

## The sessions

| Session | Role | Wake | Tool calls | Writes | End |
|---|---|---|---|---|---|
| s205 | critic | tick:review, ["bg_2"], attempt 1 | 3 loads, 3 claim True, 3 `verdicts.emit` pass | none | "repeated its previous turn verbatim twice; ended" |
| s206 | critic | the same, attempt 2 | 3 loads, 4 claim, 4 emit pass | none | "verdicts.emit was refused the same way in four turns" |
| s207 | critic | the same, attempt 3 | 3 loads, 4 claim, 4 emit pass | none | the same as s206 |
| s208 | liaison | tick:quarantined, "1 abandoned: review for bg_2 (critic), 3 attempts" | `msg.present_principal` | page m84 | after the cycle |

## What bg_2 got before the review tick

- Developer commits landed in s176 (`batches` bg_2 v4), s197 (v5) and s204 (v6). The head is 905345ed. s178, s189, s190 and s191 landed no batch receipt.
- s189 to s191 were the `verdict_failed` round after s188's fail. They ended in quarantine, s192, page m75. His answer m76 kept the change and re-worded lines 3 and 4. s195 re-specified `cr_2` v6 and `cr_3` v7.
- Tests: s179 wrote `tst_confirm_default_on_eof`, `tst_confirm_no_wait_on_eof` and `tst_confirm_help_documentation`. s181, s183, s187, s199, s201 and s203 re-encoded them. All three pass at 905345ed (`test_runs` tr144 to tr146). The log shows "37 test(s), 0 not passing" before the CYCLE line.

## The doors

| Frame | Door | Fired | Sessions and refusal text | Refusals |
|---|---|---|---|---|
| 283 | commit door, note check | yes | s189 "your code.write in this reply returned a note before this commit, and you had not read it". s189, s191, s197 "a code.write in an earlier reply returned a note, and the tree still does not hold those lines" | 11 |
| 304 | encode door, raising arrange line | plausible | s196 "this test closes sys.stdin, and pytest's own stdin goes with it: the test fails against any code". The text matches the frame's intent. I did not read the door code. | 1 |
| 305, 272 | Liaison line reader | the door ran, no defect seen | s152 "line 3: the words do not fault bg_1's files. Approve line 3." s162 "lines 1, 2, 3 have no ruling". s193 "line 5: the words do not fault bg_2's files. Approve line 5." I did not check line placement against the page. | 3 |
| 308 | ruling answer door | yes | s175 `msg.answer_tester` "no change built from this criterion has a commit yet, so the Tester has written no test of it", 4 times, session ended. s195 wrote `cr_2` and `cr_3` and one answer passed | 4 |
| 301 | confirm under CliRunner | no | no refusal text in walk 2 | 0 |
| 297 | quarantined write read as code | no sign | s189 and s191 end with "The runner discarded the writes that no commit held". s197 woke on a tick, not a relay. Not traced further. | 0 |
| 303 | textless propose as a request row | no | no `propose` call in walk 2 | 0 |
| 302 | path the index does not hold | yes | s159 `batches.guess` "confirm names no path. A symbol is written path::name. The index holds src/click/termui.py::confirm" | 1 |

## After

- The batch is not quarantined. `batches` bg_2 has status `running` at head 905345ed. The review tick is quarantined: `tick_attempts` `critic|tick:review|bg_2` attempts 3, quarantined 1.
- The log after the CYCLE line has one page, m84 "The team stopped work on this change." His answer: "Please don't drop this change. Fix line 3 and try again." The log ends there at 21:07.
- The database shows s209 `rulings.rule` (ruling r_9b2fa6b320) and s210 two `msg.relay_terminologist`. No later session exists.

## Findings

1. `rota/roles/api.py:12554`, high, CONFIRMED. The docstring refusal fires on a criterion that asks for a docstring. s205 to s207 and s198, s200 show 13 equal refusals and no verdict. Fix: skip the docstring refusal when the criterion text names a docstring, help text or documentation.
2. Outside the points, high, CONFIRMED. `cr_2` and `cr_3` v6 and v7 by s195 describe the tests, not the code. `cr_2` reads "Line 3's check must close stdin first" and "not just repeat my note about the check". His words about a test became criterion text. Fix: route a note about a check to the test, and keep the criterion on behaviour (frames 306 and 310).
3. Outside the points, low, CONFIRMED. Page m84 says "The team stopped work on this change", as m75 and m45 did. The review never objected. Fix: name a review with no verdict as a review that did not finish.

## Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad/c3_p1.py` to `c3_p8.py`: read-only queries with `?mode=ro` on sessions, tick_attempts, tool_calls, turns, verdicts, criteria, receipts, batches and test_runs. `c3_p7.py` collects every runner account line of s152 to s207.
- `grep` on `.rota/night160.log` and on `plans/stack.md` for the frame headings.

## Usage

About 70k input tokens and about 9k output tokens, about 79k in all, against the 30k cap.
