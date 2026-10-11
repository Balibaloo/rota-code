# Night 140 read

Night 140 ran cold from `C:/Users/roman/rota_night140` at 3f2e974e, 2026-10-11 17:00 to 19:36, three sentences, the agent principal on Opus. The holding session stopped it in walk 3, after `plans/night140-cycle-bg2.md` showed that bg_2 cannot merge. Rota workflow throughout. Database `.rota/clickI_night140.db` with its WAL, opened `mode=ro`. Log `.rota/night140.log`. Principal record `.rota/clickI_night140.principal.jsonl`, 38 `call` rows of night 140. Phases by the request sessions: onboarding s1 to s177, walk 1 s178 to s231 (m_p1), walk 2 s232 to s294 (m_p2), walk 3 s295 to s326 (m_p3). Scripts: the scratchpad folder `n140` of session 59bdd13a. Read 2026-10-11 by an agent of session 59bdd13a. Not committed.

Verdicts, one line each:

- Q1. 326 sessions, 1,344 turns, 196 messages, 38 principal calls, 5.27 dollars. 1 merge of 3 sentences. Sentence one never reached a batch. Sentence two merged as bg_1 after 7 attempts. Sentence three stopped at attempt 2.
- Q2, frame 200. The measure, attempts to a merge on bg_2, is not reachable. bg_2 ran 2 attempts. Attempt 1 was red on the inherited test `inh_f3b0c3db` alone. Attempt 2 added two Tester tests that read `.callback` on the decorator. Frame 200's door admits that shape (CONFIRMED by a probe). The answer-mode door and the three-ref hint had no case.
- Q3, frame 197. 0 of 38 answers lost from this cause. One session, s94, showed the sign, read the new refusal, and landed. 1 of 38 lost for another cause, m127. Baseline 1 of 43.
- Q4, frame 195. 0 of 7 Developer `tests_failing` sessions show an empty-output red. Every red names its exception. 0 attempts end red on a hidden exception. No test used `CliRunner.invoke`, so the plugin had no case. Baseline 10 of 11.
- Q5, frame 169. 1 of 4 distinct refusal lines after an eviction is false, s304 turn 5. Baseline 2 of 6. Target at most 1 in 10. The cause is a substring match on the answer `[]`, not the eviction path the frame fixed.
- Q6, frame 204. 64 fresh notes: Vision Keeper 40, Terminologist 12, Tester 8, Liaison 2, Critic 1, Developer 1. Faults and blocks 8, traces 43, echoes 4.
- Q7. The principal misread 0 of 38 pages. Three pages carried a seat's fault, and the principal named each fault.
- Q8. 116 sessions hold zero receipts. 88 of them sent a message, which writes no receipt. 28 did no admitted work, in 7 shapes.

## 1. The night's shape

(observed: `shape.py`, the log, `items`, `item_parks`, `tick_attempts`, `sessions`)

| Phase | Clock | Sessions | Turns | Steps, asks | Principal calls, dollars | End |
|---|---|---|---|---|---|---|
| onboarding, cold | 17:01 to 18:00 | s1 to s177, 177 | 676 | 198 steps, 16 asks | 16, 2.29 | `ONBOARDED`, then the Stuck line |
| walk 1, `echo_json` | 18:00 to 18:12 | s178 to s231, 54 | 189 | 63 steps, 9 asks | 9, 1.25 | `quiet`, a page waits on the principal |
| walk 2, `confirm default_on_eof` | 18:12 to 19:07 | s232 to s294, 63 | 337 | 78 steps, 8 asks | 8, 1.08 | `MERGED (1 total)`, bg_1 |
| walk 3, `version_option show_python` | 19:07 to 19:36 | s295 to s326, 32 | 142 | not logged | 5, 0.65 | stopped, bg_2 `running` at attempt 2 |

- Batches: bg_1 on `confirm_default_on_eof`, merged, 7 attempts (`max(test_runs.attempt)`). bg_2 on `version_option_show_python`, `running`, 2 attempts. No batch for `echo_json`.
- Sessions by role: Vision Keeper 118, Liaison 113, Terminologist 39, Architect 18, Critic 15, Tester 14, Developer 9.
- The log holds 2 CYCLE lines. Onboarding: `vision_keeper|tick:contested||["defines_commands_and_options"]`. Walk 3: `developer|tick:tests_failing|attempt 1|["bg_2"]`, the inherited red of the cycle read.
- The Stuck line, after onboarding and after walk 2: `Stuck. The team gave up on: contested for parses_and_executes_inputs. Nothing waits on you, and nothing moves until that is cleared.` The line is false twice. The item `parses_and_executes_inputs` is `approved` (observed: `items`), and walk 2 merged bg_1 after the line. The line reads the quarantined tick `vision_keeper|tick:contested|parses_and_executes_inputs` (attempts 3, quarantined 1), not the item's state (reasoned).
- Sentence one's shift. Walk 1 ended `quiet` because the Liaison s228 lost the answer m127 (section 3). Page m126 stays open. When m_p2 landed, the shift page asked about `echo_json`. The principal answered m132: "Later. Put the JSON helper aside until the new request is merged". `item_parks`: park at m133 (seq 136), resume with cause m_p2 (seq 177), park again at m179 (seq 184), on the m_p3 shift page and the same word "Later". So the principal's word parked sentence one twice, and the night never built it. The resume after bg_1's merge did what the principal said (observed: `item_parks`, the log lines 68 and 108).
- `tick_attempts` now reads `developer|tick:tests_failing|bg_2` 1, quarantined 0. The cycle read saw 3 and 1 at 19:30. The principal's m190 reset the tick (reasoned: the quarantine page s323 and the answer m190 come between the two reads).

## 2. Frame 200's doors on bg_1 and bg_2

**The Tester's stored tests** (observed: `tests`, `test_runs`).

| Test | Batch | What it does | Runs the behaviour? |
|---|---|---|---|
| `tst_cr1_closed_stdin_returns_default` v3 | bg_1 | swaps `sys.stdin` for an empty `io.StringIO`, then calls `confirm(..., default_on_eof=True)` | yes |
| `tst_cr2_false_stdin_aborts` v6 | bg_1 | patches `visible_prompt_func` to raise `EOFError`, expects `Abort` | yes |
| `tst_cr3_open_stdin_no_effect` v1 | bg_1 | monkeypatches stdin to a `y` line | yes |
| `tst_v1_show_python` v1 | bg_2 | `option = version_option(show_python=True)`, then `option.callback(None, None, True)` | no |
| `tst_v3_show_python` v1 | bg_2 | the same with `False` | no |

- No bg_1 test applies a decorator to a plain function. Every bg_1 test calls `confirm` (observed).
- Both bg_2 tests never run the behaviour. They call the factory, read `.callback` on the decorator it returns, and fail with `AttributeError: 'function' object has no attribute 'callback'` (observed: tr111, tr112). This is the shape of nights 138 and 139, a factory return that never decorates a command, in a fourth form.
- Frame 200's door admitted the two tests. A probe ran `_plain_decorated` and `_factory_misuse` from the night's tree on both stored bodies. Both return `None` (CONFIRMED: `p_door.py`). `_plain_decorated` at `rota/roles/api.py:5958-5993` reads a bare return that is called, or passed to a call. It does not read an attribute of it, such as `option.callback`.
- The same door refused the third test, `tst_v2_show_python`, which held `assert callable(option)`: "`option` is the decorator that `version_option` returns, and passing it to a call never runs the option". So `c2_version_option_show_python` has no test, and s325 sent 33 encodes in one session (observed: s325's turns).

**The Developer's challenges and escalations** (observed: `messages`, `tool_calls`, the turns).

| Session | Call | What it carried | Outcome |
|---|---|---|---|
| s291, bg_1 attempt 6 | `msg.challenge_tester` | `cr_2`, `tst_cr2_false_stdin_aborts`. The test expected `EOFError`, and the code raises `Abort` | landed as m173. The Tester s292 re-encoded the test (v6). bg_1 then merged |
| s322, bg_2 attempt 1 | `msg.challenge_tester` twice | `c1`, `c2`, `c3`, `inh_f3b0c3db`, the `DeprecationWarning` line | refused both times: the inherited test has no criterion |
| s326, bg_2 attempt 2 | `msg.challenge_tester` | `c1_version_option_show_python`, `tst_v1_show_python`, with c2's text as the quote | landed as m191, `open` at the stop |
| s326 | `msg.challenge_tester` five more times | `c3`, `tst_v3_show_python`, and repeats | refused: "you have already sent challenge to tester; saying it again with different refs is a second answer". The second wrong test has no route in that session |

- Escalations: 0. No Developer called `msg.escalate_architect` (observed: `tool_calls`).
- No answer to a Developer was written. Six answers to Tester questions carry refs and no words: m158, m161, m169, m171 by the Terminologist, and m166, m172 by the Vision Keeper (observed: `messages.body_text` NULL).
- The answer-mode door and the three-ref hint had no case. No Developer session woke on a message. All 9 Developer sessions woke on `tick:batch_start` or `tick:tests_failing` (observed: `sessions.wake_kind`).

**The measure.** Attempts to a merge on bg_2 cannot be reached. The night stopped at attempt 2 with no merge.

- Attempt 1, 37 tests, 1 red: `inh_f3b0c3db`. The test is bg_1's own `tst_cr1`. It is red at the base under the project's `filterwarnings = ["error"]`, because the harness drops the `DeprecationWarning` ignore flag once a test has no criterion (copied: `plans/night140-cycle-bg2.md`, sections 2 and 3). s320, s321 and s322 read the red, and none had an admitted call that clears it. Then the tick was quarantined, and the principal said in m190 "Please don't drop this change".
- Attempt 2, 39 tests, 3 red: `inh_f3b0c3db` again, and the two `.callback` tests. s326 sent one challenge, m191.
- So bg_2 has two walls: frame 114's inherited red with the harness flag flip, and a wrong Tester test that frame 200's door admits (reasoned).

## 3. Frame 197: `words` inside `rulings`

(observed: `ans.py`, `rulings` by `reply_id`, `tool_calls` where `rulings` holds a `words` key, the turns of s94 and s228)

- 38 principal answers: 16 in onboarding, 9 in walk 1, 8 in walk 2, 5 in walk 3. The three requests are not answers. 37 drew a landed ruling.
- 1 call series put `words` inside `rulings`: s94 on m12, calls 1 and 2. The new refusal said: "rulings has a key words, and words is its own argument, not a line of the page: rulings.rule(rulings={...}, words=...)". Call 3 moved `words` out. Call 4 ruled every line and landed `r_7215eb61a9`. The mechanism worked on its first night case.
- Ratio: 0 of 38 answers lost from this cause. Baseline 1 of 43. Target 0 of the next 40, so the count holds with 2 answers still to come.
- Residue: 1 of 38 answers lost, m127. The page m126 had 1 line. The principal asked about "lines 2 to 5 from the last page". s228 ruled lines 1 to 5. The door refused "'2' is not a line of the page", the seat repeated the call verbatim, and the repeat door ended the session. The cause is a line number the page lacks, the shape of night 139's m142, not frame 197's. The loss left walk 1 quiet and sentence one unbuilt (reasoned).

## 4. Frame 195: the hidden exception

(observed: `f195.py` on turn 1 of each Developer `tests_failing` session, `test_runs`)

| Session | Batch, attempt | The red in turn 1 |
|---|---|---|
| s269 | bg_1, 3 | `AttributeError: 'ClosedStdin' object has no attribute 'readline'` |
| s270 | bg_1, 3 | the same |
| s291 | bg_1, 6 | `click.exceptions.Abort`, `1 failed` |
| s320, s321, s322 | bg_2, 1 | `DeprecationWarning: 'isolated_filesystem' is deprecated` |
| s326 | bg_2, 2 | 2 times `AttributeError: ... 'callback'`, and the `DeprecationWarning` |

- 0 of 7 sessions show an empty-output red. Baseline 10 of 11 on night 138's b_3. Target at most 1 in 5. Holds.
- 0 attempts end red on a hidden exception, of 9 attempts in all, 7 on bg_1 and 2 on bg_2.
- No turn holds the plugin's section title, `CliRunner caught an exception`. No test called `CliRunner.invoke`, so the plugin had no case (reasoned: the five test bodies in section 2). The ratio holds, but this night did not exercise the mechanism.

## 5. Frame 169: false `in this prompt` sentences

(observed: `f169.py` to `f169e.py` over `turns.user`)

- 88 turns carry the eviction notice, `dropped to fit the window`. 6 turn copies of `The answer is in this prompt.` stand after an eviction. They are 4 distinct refusal lines: s304 turn 5, s319 turn 10, s320 turn 9, and s322 turn 8, which stays in turns 9 and 10.
- s319, s320 and s322: the answer stands. s319's `code.source` 420 to 558 was served again in the same prompt. s320 and s322 hold their `OK code.commit` lines.
- s304 turn 5, a Critic on `tick:challenge`: false. `code.probe(pattern='def confirm')` was refused, and no `code.probe` answer stands in the prompt after 6 exchanges were dropped.
- The new sentence fired in s314 turns 9 to 11: "The window dropped the answer after this line, so ask once more and it is served again" (observed).
- Ratio: 1 of 4 lines, or 1 of 6 copies. Baseline 2 of 6. Target at most 1 in 10. Fails on the count.
- Residue, the cause of s304: `_repoint` keeps the sentence when `answer in user` (`rota/core/runner.py:748`). The answer is `_render([])`, the string `[]`. The string stands 3 times in s304's turn 5, inside `cited: []` of the pushed `challenge.load` block (CONFIRMED: a probe on the night's tree printed `'[]'`, `in user: True count 3`). So a short answer matches by substring and hides the drop. This is a new cause, not the eviction path of the frame.

## 6. Frame 204's baseline

(observed: `f204.py`, which runs the rules of `classify.py` from `plans/frame204-corpus.md` section 1 on night 140's `ledger`, writer from `receipts`)

The night is cold, so all 64 rows are fresh.

| Author | Rows | Masses |
|---|---|---|
| Vision Keeper | 40 | F 40 |
| Terminologist | 12 | D 8, E 4 |
| Tester | 8 | B 4, C 2, F 2 |
| Liaison | 2 | H 2 |
| Critic | 1 | G 1 |
| Developer | 1 | F 1 |

- The kinds the seats wrote: `default` 62, `unaddressed_answer` 2. No other kind exists, because frame 204's `kind` enum is not in 3f2e974e (copied: `plans/stack.md`, frame 200, status 16:46).
- Faults and blocks, mass D: 8, all by the Terminologist. Blocked by the record: 7, a glossary row that does not exist (`l_075089207c`, `l_c3bb70a620`, `l_e2d18a6502`, `l_65644d743f`, `l_045d2e3137`, `l_96e1aedca0`, `l_f14c6f8a60`). Fault proper: 1, `l_4386ea61e9`, `glossary.adopt` on a criteria row.
- Traces, mass F: 43. 36 of them are the Vision Keeper's `tick:reconcile` rows, "the README says X; the code shows Y". The corpus has no mass for them, so its rule files them as F by default. They are a ninth mass, reconcile findings (reasoned). The other 7 are 3 Vision Keeper item restatements, 3 Tester notes and 1 Developer note.
- Echoes, mass E: 4, the Terminologist on relays s261 and s286. `l_96b433cd49` reads as a fault by content.
- Real choices, mass C: 2, Tester s266. Dictated literals, mass B: 4. Critic G: 1. Unaddressed H: 2.
- Misfile: `l_0842c04377`, Tester, "cannot be encoded because confirm() binds visible_prompt_func at import time", is a fault by content. The rule misses "cannot be encoded".
- Status: 42 resolved, 22 open.

## 7. The agent principal

(observed: the log, the principal record's `call` rows, `rulings`)

| Page | Kind | Answer, in short | Read right? |
|---|---|---|---|
| m2 | present | ok, a fair description | yes |
| m6 | present | ok; lines 13 to 23 are kinds of users | yes |
| m11 | present | lines 2, 3, 8 quote labels, not the README | yes |
| m15 | present | line 3 a label; line 4 wrong, decorators do define commands | yes |
| m21 | present | ok | yes |
| m26 | present | lines 3, 4 cite Briefcase; line 5 repeats line 1 | yes |
| m30 | present | line 2 an unfounded claim; lines 5 to 8 mispaired | yes |
| m36 | present | lines 3 to 5 Briefcase; lines 2, 6, 7, 8 mispaired | yes |
| m43 | clarify | approve `how_it_works` | yes |
| m47 | clarify | keep `parses_and_executes_inputs` | yes |
| m51 | present | ok | yes |
| m55 | present | lines 3, 7 wrong; line 4 repeats line 2 | yes |
| m60 | clarify | the invoice and card question is from another project | yes. The page was the seat's fault |
| m70 | clarify | include the CLI item | yes |
| m73 | present | ok | yes |
| m77 | present | line 2 is wrong, I did answer that question | yes. Line 2 was the false `unaddressed_answer` note `l_11113fad2c` |
| m81 | confirm | ok | yes |
| m86 | present | line 3 cut mid-word; the code pointer lacks the utilities module; standard json only | yes |
| m92 | clarify | the line 3 text; put the helper after echo; export it | yes |
| m97 | present | line 1's pointer still lacks the module | yes |
| m102 | clarify | yes, add the module to the pointer | yes |
| m108 | present | restore line 3; keep my request text | yes |
| m113 | clarify | the README needs no change; restore both lines | yes |
| m119 | present | take the pointer out of my request | yes |
| m126 | present | the text is right; the list lacks the module; where are lines 2 to 5? | yes. The answer was lost, section 3 |
| m128 | confirm | ok | yes |
| m_shift_echo_json_m_p2 | present | Later, until the new request merges | yes |
| m135 | present | line 2 lacks off by default | yes |
| m142 | present | line 3 is my pasted reply, not an assumption | yes. Line 3 was `l_b2d0199f1b` |
| m147 | clarify | yes, remove line 3 | yes |
| m152 | clarify | the two behaviours do not conflict | yes |
| m155 | present | ok | yes |
| m162 | clarify | flag off aborts as now | yes |
| m174 | confirm | ok | yes |
| m_shift_echo_json_m_p3 | present | Later, until show_python merges | yes |
| m181 | present | ok; take the version from `sys.version_info` as major.minor.micro | yes. It adds a detail the sentence lacks |
| m185 | present | line 2 lacks that format; the flag defaults to off | yes. It restates its own m181 detail |
| m189 | present, quarantine | every line is right; do not drop; fix the tests | yes |

- 38 calls, 5.27 dollars, 0 errors (observed: `pj2.py`).
- 0 misreads. The principal added one detail of its own at m181, the `major.minor.micro` format. The Terminologist put the format into c1 by m189 (observed: m189's line 2). That is a principal choice, not a misread (reasoned).

## 8. Residue: sessions with zero receipts

(observed: `res8.py` and `res8.out`: `receipts`, `tool_calls`, the account in each session's last turn)

116 of 326 sessions hold zero receipts. A message writes no receipt (observed: m191 landed from s326, and s326 holds none). 88 sessions called `msg.*` and are the designed shape of their wake: Liaison present, relay, clarify and quarantine pages, and Vision Keeper sign-offs. The other 28 did no admitted work. The causes, grouped by shape:

1. Relay wake with no admitted act, 7. Architect s91, s96, s100, s119, s125 and Terminologist s126 were refused by the ruled-row `ledger.log` door. Terminologist s120 was refused by `glossary.adopt`, "you named none". The door stopped an echo, and the seat had no other act.
2. Vision Keeper `tick:contested` loop in onboarding, 9. s105, s106, s128, s133, s134, s135: `decisions.author` refused an item id as a decisions row. s136, s143, s144: a verbatim repeat. This loop fed the quarantine and the false Stuck line.
3. Liaison report with nothing to relay, 2. s104 and s142 quoted the transcript and ended with prose. No call followed.
4. Liaison lost answer, 1. s228 on m127, a line number the page lacks (section 3).
5. Tester encode refusals on bg_1's cr_2, 5. s271, s281 and s288: "every assertion here is on a constant". s275: "pytest will collect nothing". s285: "the test uses click and never imports it".
6. Developer invalid writes, 1. s269 on bg_1: "src/click/termui.py is not valid Python (unexpected indent, line 327)".
7. Developer on bg_2's inherited red, 3. s320 ended "with nothing done". s321 ended on the `code.commit` repeat. s322's two challenges were refused, and it ended on the same repeat (copied: `plans/night140-cycle-bg2.md`, section 4).

Not read further: s271 and s281 hold identical 11-call lists, and s272 and s282 identical 26-call lists. Two wakes on one prompt gave one output twice (observed: `build.py`).

## Findings outside the points

1. `rota/roles/api.py:5958-5993`, `_plain_decorated`. High. CONFIRMED by `p_door.py`. The door admits `option = version_option(...)` then `option.callback(...)`, a factory return that never decorates a command. Fix: treat an attribute read on a bare factory return as the "decorator" kind.
2. `rota/core/runner.py:748`, `_repoint`. Low. CONFIRMED by a probe. `answer in user` matches the short answer `[]` in an unrelated block, so a false `in this prompt` sentence stays. Fix: look for the answer's own result line, not a bare substring.
3. The challenge door that refuses "a second answer with different refs". Low. Observed on s326. A Developer with two wrong tests can challenge only one per session, and the second waits a full attempt. Fix: admit one challenge per test in a session.
4. The Stuck line. Low. Observed: the log and `items`. It names a quarantined tick on an approved item and says nothing moves, and bg_1 merged after it. Fix: build the line from the items still contested, not from quarantined ticks.

## Probes

All are in the scratchpad folder `n140` of session 59bdd13a. Each opens the database with `file:...?mode=ro`.

- `db.py`, the read-only query helper. `shape.py`: the counts of section 1. `tests.py`: test bodies and red outputs.
- `build.py`: Developer and Tester sessions with their calls and receipts. `turns.py` and `res.py`: turns and refusal texts.
- `p_door.py`: `_plain_decorated` and `_factory_misuse` from `C:/Users/roman/rota_night140` on the stored bg_2 bodies.
- `ans.py`: principal answers, rulings and asks. `f195.py` and `f195b.py`: the reds in turn 1.
- `f169.py` to `f169e.py`: eviction and refusal lines. One `python -c` probe of `_render([])` against s304 turn 5.
- `f204.py`: the corpus rules on the night's ledger. `pj.py` and `pj2.py`: the principal record. `res8.py`: the residue.
- `rota.tools.map fn _plain_decorated` in the night's tree. No model call, no pytest, no edit of a tracked file, nothing written into `.rota/`.

## Usage

About 115k input and 18k output, about 133k total (estimate). The harness line is the authority.
