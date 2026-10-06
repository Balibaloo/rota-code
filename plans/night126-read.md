# Night 126 read

Night 126 ran cold from `C:/Users/roman/rota_night126` at fbe4cc25, 2026-10-06 14:32 to 16:09. The tree joins frames 152, 144, 149, 153 and 151 on `rota/foundation`. It holds 249 sessions and 1,073 turns. It has three walks and 3 batches. Rota workflow throughout. Database `.rota/clickI_night126.db`, log `.rota/night126.log`. `.rota/night126.err` holds one traceback of 1,396 bytes, section 6. Scripts: the scratchpad folder `n126` of session 488d31af: `lib.py`, `state.py`, `tr.py`, `acts.py`, `msgs.py`, `q1.py`, `q2.py`, `q4.py`, `q4b.py`, `q5.py`, `q6.py`, `q7.py`, `q8.py`, `q9.py`. They read the database with `mode=ro&immutable=1`, and `lib.py` imports the parser from the night's tree (observed: the scripts, 2026-10-06).

Verdicts, one line each:

- Frame 152, a Tester writes its repair in a code block: 2 of 5 Tester challenge sessions end with no call after a reply that holds a test body. The baseline is 2 of 5. The line is at most 1 in 5. Not met. The nudge fired in 2 of 2 such sessions and moved 0 of 2. Encodes after the nudge: 0 sent, so 0 landed, against 0 of 5 in the recorded case.
- Frame 153, a door says `End the session with no call.`: the seat followed the step in 1 of 11 turns. The baseline is 3 of 7. The line is at least 3 in 4. Not met. The owed-call nudge fired 0 times after the step, so the repair held. In all 10 unfollowed turns no runner text stood between the refusal and the next call.
- Frame 149, the revert door: 0 `code.commit` calls met the revert door. 1 batch was given up, bg_1 at 10e3fa7c71, 33 pass, 4 fail, 0 error. Given up at a head that a refused revert would repair: 0 of 1. The baseline is 1 of 1 on night 124.
- Frame 151, the parser and a line break: 0 of 148 `code.write` and `tests.encode` calls lost a line break. The baseline is 12 of 1,719 on nights 113 to 124. The two new guards raised 0 refusals. 1 triple-quoted value stood on the night, and the parser read it right.
- Frame 144, the tier: the tier found 11 faults before the night. The night found 4 structural faults that the tier missed, and a scene or a catalogue row could have held 3 of them. One of the 4 crashed the night. 5 more walls are the model's judgement.
- The crash: s249, the Vision Keeper, turn 5, `problem.prioritize(id='version_option_show_python', priority='high')`, answered `OK`. No door spoke. Walk 3 made 23 steps, and the 24th crashed in `frontier`. No step can run again on this database.
- The end state: bg_1 `deferred` past the cap, bg_2 `merged` at a0d92ad4 with 36 of 36 tests passing, bg_3 `pending` and next. The exhausted ladder ran through, the park freed the place, and bg_2 ran. That is new against night 125.
- Crashes: 1. 249 of 249 sessions are committed. `CYCLE` lines: 0.

## 1. Frame 152, a Tester writes its repair in a code block and sends no `tests.encode`

**The nudge fired in both sessions that showed the sign. Neither seat sent a call after it.**

The 5 Tester challenge sessions (observed: `q2.py`, section 1, 2026-10-06):

| Session | Woken by | `tests.encode` calls | Replies with a test body and no call | Nudge | End |
|---|---|---|---|---|---|
| s141 | m64 | 5, all refused | 0 | none | `msg.answer_developer`, m66 |
| s150 | m73 | 7, 6 refused, 1 landed | 0 | none | `inh_echo_json_03` version 2, green |
| s154 | m76 | 0 | 2, turns 1 and 2 | turn 1 | no call |
| s156 | m77 | 2, both refused | 3, turns 1, 4 and 5 | turn 4 | no call |
| s170 | m84 | 3, all refused | 0 | none | `msg.answer_developer`, m85 |

The nudge's text, s154 turn 1: `You wrote a test into your reply, and a reply is not a stored test -- nothing landed. Send it as a call: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', path='tests/test_utils/test_echo_json_compact.py', body='...').` In s156 turn 4 the text opens `You wrote code into your reply` and ends `, or end by saying nothing is owed.` Both name the id, the criterion and the path (observed: `q2.py`, 2026-10-06).

**s154, 2 turns.** Turn 1 holds the test in a fence and 0 calls. Turn 2, after the nudge, holds the same test in a fence and 0 calls. Its words, lines 1 to 3:

```
The test fails because `runner.invoke` expects a Click command object (which has a `.name` attribute), but `echo_json` is imported as a plain Python function. The criterion does not specify that `echo_json` must be wrapped ...

I will encode a corrected test that wraps `echo_json` in a `@click.command()` decorator before invoking it. This ensures that `runner.invoke` receives a valid Click command object.
```

The reply says `I will encode a corrected test` 4 times in 46 lines and ends mid-word. The runner's account: `wrote a test into its reply`. The nudge moved nothing (observed: `q2.py`, section 1b, 2026-10-06).

**s156, 6 turns.** Turn 1 is 34,236 characters. The runner cut it: `CUT your reply: 30,236 of 34,236 characters are not shown. The first 4,000 characters stand above. No call in your reply ran. Send one call, and keep your prose short.` and `ERROR reply cut: ... It held no whole call, so no call ran and nothing was written.` No test nudge stood after turn 1. Turns 2 and 3 sent `tests.encode`, and the not-Python door refused both, section 9, wall 2. Turn 4 is 34,509 characters, cut again, and the nudge followed it. Turn 5 is 32,166 characters of prose, cut again, with 0 calls. The session ended there (observed: `q2.py` and `q5.py`, 2026-10-06).

The cause in both is the seat, model `qwen3.5:9b`: it names the act and does not perform it, and in s156 it writes past the output budget three times in five replies (reasoned: the replies above). The repair's mechanism holds. The sign stays at 2 of 5, and the residue has one more part than the frame named: the reply cut stands where the nudge would stand after a reply with no whole call (reasoned: s156 turn 1 got the cut sentences and no nudge).

## 2. Frame 153, a door says `End the session with no call.`

**The runner's nudge never followed the refusal. The seats sent the next call anyway, with no text of the runner between.**

Every turn that met the step (observed: `q2.py`, section 2, 2026-10-06):

| Met at | Attempt | Between the refusal and the next call | The next turn | Followed |
|---|---|---|---|---|
| s159 t11 | 4 | nothing | `code.write` | no |
| s166 t1 | 6 | nothing | `code.write`, `msg.escalate_architect` | no |
| s167 t1 | 7 | nothing | `msg.escalate_architect` | no |
| s167 t10 | 7 | nothing | prose, 0 calls | yes |
| s168 t1 | 8 | nothing | `code.write` | no |
| s168 t11 | 8 | nothing | `ledger.log`, the same challenge | no |
| s168 t12 | 8 | the `NOTE ... will not be accepted again` | the same challenge, 4 copies, made-up results | no |
| s169 t1 | 9 | nothing | a challenge on other refs, landed as m84 | no |
| s172 t2 | 10 | nothing | the same challenge | no |
| s172 t3 | 10 | nothing | the same challenge | no |
| s172 t4 | 10 | the `NOTE` | the same challenge, 3 copies, made-up results | no |

- The owed-call nudge, `You were woken because something is owed here`, fired 2 times on the night, once for a Liaison and once for a Terminologist, and 0 times for a Developer (observed: `q2.py`, section 6, 2026-10-06). So the `EndRefusal` held in 11 of 11.
- The residue is the cause that the frame's brief named from s156 of night 125: the seat sends a call again with nothing between. 10 of 10 unfollowed turns have that shape.
- s169 turn 2 is a case of its own. After the step said end, the seat challenged `inh_echo_json_02` on other refs. The call landed as m84, the Tester s170 answered it, m85, and the Developer s171 woke on the answer. The step was wrong for that session (reasoned: the rows of m84 and m85).
- The escalation door's choice, `make one real change to the code the test calls, or end the session with no call`, stood 5 times, in s166 and s167. No nudge followed it, because none fired for a Developer. Frame 159 had 0 cases.

## 3. Frame 149, the revert door

**The door had no case. The one given-up batch ended at a head where a revert would be admitted, and no seat tried one.**

- `code.commit` result lines on the night: 21 `committed: true`, 18 `committed: False, why: nothing changed`, 8 `asked three times`, 5 `unchanged since you asked`. 0 lines hold `undoing yourself`, `going back` or `The tests pass both ways` (observed: `q2.py`, section 3, 2026-10-06).
- Batches given up: 1. bg_1 went `deferred` by `do:park: deferred bg_1; its ladder is spent`, the first scheduler action of walk 2. Its head is 10e3fa7c71 at attempt 11, past the cap of 10. The runs at that head: 33 pass, 4 fail, 0 error. The red tests: `inh_echo_json_01`, `inh_echo_json_02`, `inh_echo_json_03`, and the project test `inh_55974267`, `tests/test_imports.py::test_light_imports`, `assert 'json' in {...}` (observed: `state.py`, `q1.py`, the log, 2026-10-06).
- Would a revert repair that head: going back from 10e3fa7c71 to a87f92903a turns `inh_echo_json_03` green and no test red, so the door would admit it. No commit of the night put a tree back (reasoned: the runs of the two heads in `test_runs`, and the 0 refusals).
- The head that failed at import: b9e515bfdf, attempt 5, 37 of 37 `error`. s164 turn 4 wrote `@click.command()` above `echo_json` with no `click` name in the module, and the write door admitted it. That is frame 146's sign, 1 case. s165 repaired it forward in 4 commits, and the next run, 74a8aaefc3 at attempt 6, had 3 fail and 0 error. Frame 161's case, a first commit that fails at import, did not occur: b9e515bfdf was the third commit (observed: `q1.py`, the red runs, and `dev1.out`, 2026-10-06).

The heads and the runs of bg_1, in order (observed: `state.py`, 2026-10-06):

| Head | Attempt | Fail | Error | Session |
|---|---|---|---|---|
| 972e707141 | 2 | 2 | 0 | s130 |
| ce9a59874c | 4 | 2 | 0 | s143 |
| b9e515bfdf | 5 | 0 | 37 | s164 |
| 74a8aaefc3 | 6 | 3 | 0 | s165 |
| 783f542914 | 7 | 3 | 0 | s166 |
| dbf0c9cc96 | 8 | 3 | 0 | s167 |
| 653a9f0b62 | 9 | 3 | 0 | s168 |
| a87f92903a | 10 | 3 | 0 | s171 |
| 10e3fa7c71 | 11 | 4 | 0 | s182 |

From attempt 6 on, one of the three reds is the project test `test_light_imports`, because the Developer put `import json` at module level. No seat read that red as its own (observed: the four red outputs at each head, `q1.py`, 2026-10-06).

## 4. Frame 151, the parser and a line break

**No call lost a line break. The night's one triple-quoted value read right. The guards had no case.**

- `q4.py` runs every completion through the night tree's `extract_lenient` and finds 148 `code.write` and `tests.encode` calls with a string value. It then finds the value's first and last line in the completion and compares the line breaks. 115 values hold more line breaks than the raw text, because the seat wrote the call on one line with `\n` escapes, and the parser turns each into a line break. That is the right read. 1 is equal. 32 the instrument could not match or marked as lost (observed: `q4.py`, 2026-10-06).
- `q4b.py` prints the 32 beside their raw calls, 10 distinct bodies. Each parsed value is what Python reads from the seat's text: `\"` becomes `"`, `\\n` becomes `\n`, `\\'` becomes `'`. The instrument's raw region ran into prose or into the next call. Lost line breaks by hand: 0 of 10 bodies, so 0 of 148 (observed: `q4b.out`, read by hand, 2026-10-06).
- Triple-quoted values opened on the night: 1. s80 turn 6, the Critic, `challenge.uphold(..., why='''The claim states that UNSET is a sentinel value cited in these files. ... docstring "Sentinel used to indicate that a value is not set." ...''')`. The value holds double quotes and no line break, and the parser read it whole (observed: `q4.py` and `q5.py`, 2026-10-06).
- The guard on joined strings, `a quote inside a value closed it early, and the text after that quote was read as a second string`: 0 refusals. The third reading's doubts: 0 refusals (observed: `q4.py`, the parser refusals by first words, 2026-10-06).

The parser refusals of the night, 13 lines (observed: `q4.py`, 2026-10-06):

| Count | Text, in short | Where |
|---|---|---|
| 5 | `could not parse arguments: invalid syntax (<unknown>, line 1)` | s140 t5, t6; s155 t5, t12; s159 t10, each a `msg.challenge_tester` with `separators=(",", ":")` inside a double-quoted quote |
| 2 | `could not parse arguments: body= opens with ' and never closes` | s139 t1, t2, a body with `can\\'t`, where the string closes early |
| 2 | `unterminated argument list: a quote inside a quoted argument ended the string early` | s106 t1, s169 t3 |
| 2 | `unterminated argument list: the value of <key> never ends` | s45 t3 `assumption`, s80 t5 `why` |
| 1 | `a quote inside text ended it early` | s130 t11 |
| 1 | `could not read an argument name` | s210 |

The 5 `invalid syntax` refusals name no argument and no quote. The seats recovered by writing `(',', ':')` in place of `(",", ":")`, s155 t6 and s159 t11, and those calls landed. The 2 `never closes` refusals describe a string that closes early. Both are frame 137's shape, a parser refusal that names a wrong thing or nothing (reasoned: the texts and the raw calls in `q4b.out`).

## 5. Frame 144, the scenes and the instruments as a test tier

**The tier found 11 faults before the night. The night found 4 structural faults the tier missed, and 3 of them fit a scene or a catalogue row.**

Faults the tier found before the night, from the stack's own words on how each was found: frame 162's 4, by the follow check and the fact check; frame 148's 3, by the follow check as strict xfails; frame 151's 1, by the fuzz slice; frame 163's 1, by the Critic scene; frames 155 and 156, 2, by the fuzz and the replay in frame 151's reviews. 11 (reasoned: the headings and first lines of frames 148, 151, 155, 156, 162 and 163 in `plans/stack.md`). Frame 144's status of 2026-10-05 21:56 counts 10 found with no night, 4 of them with no frame (copied: `plans/stack.md`, frame 144).

What the night found that the tier missed, and which scene could have held the state (reasoned: the scenes' builders in `rota/testkit/scenes.py` and the states below):

| Wall of the night | Kind | A scene that could hold it |
|---|---|---|
| `problem.prioritize` admits a string, and `next_batch` crashes, section 6 | structure | `two_batches`: it builds items with a priority through `item(sc, n, priority)`. A catalogue row `problem.prioritize(id=..., priority='high')` and one `loop.step` would crash the scene |
| The not-Python door of `tests.encode` names a wrong cause and no step, 12 refusals, section 9 wall 2 | structure | any scene with a Tester wake and a catalogue row whose body holds `["{\"key\": \"value\"}"]` once escaped. The fact check reads `line 6` as true. The sentence `not a description of one` is not a fact the check reads |
| The relay carries a batch id to the Vision Keeper's approve step, section 9 wall 3 | structure | the park scene holds a batch past the cap. The ladder's end, `tick:exhausted` for the Architect and the Vision Keeper, the report, the clarify and the relay back, is not built. A scene that runs the ladder to its relay would hold it |
| The same-refs step says end while a challenge on another red test lands, s169 | design | `challenged` holds one test at version 2. A scene with two red tests, one under the bound, would hold it. The rule is open |

Walls that are the model's judgement, which no scene holds: the Tester's reply with a test and no call, section 1. The Developer's call after `End the session with no call.`, section 2. 19 commits that wrap or rewrite `echo_json` to fit `CliRunner`, frame 131. The Vision Keeper's new item from a criterion's words, frame 129. 84 made-up turns, frame 113 (reasoned: each is a seat's reply to a prompt that held the fact).

The night's one crash is in the first row. The nine invariants of pass 9, run at the end of every night, would have found the text in `items.priority` after the crash. A catalogue row finds it before a night (reasoned: an invariant reads the row, a catalogue row sends the call).

## 6. The crash of walk 3

**One Vision Keeper wrote `'high'` into an integer column, no door spoke, and the scheduler's sort died on the next step.**

The writer (observed: `tr.py 600 300 s249`, `q1.py`, `q5.py`, 2026-10-06). s249 is a Vision Keeper woken by m145, the Liaison's relay of the principal's answer m144. The relay's refs are `["tk_1_version_option_show_python"]`, a ticket, with `principal_verdict: {"tk_1_version_option_show_python": "approve"}`, `principal_said: "the Python version comes from sys.version_info as major.minor.micro"`, and a `resolved_refs` block that names `item_id: version_option_show_python` and `table: tickets`. The turns:

1. `TOOL: problem.set_approval(id='tk_1_version_option_show_python')`. `ERROR problem.set_approval: problem.set_approval: missing required argument(s) ['approval']; accepts (id, approval)`.
2. The same with `approval='approved'`. `ERROR problem.set_approval: 'tk_1_version_option_show_python' is already a row of tickets; an artefact id is unique across every artefact table, or every ref to it is ambiguous. Give this items row an id of its own, a short name for what it says, and send again`.
3. `TOOL: problem.prioritize(id='tk_1_version_option_show_python', priority='high')`. The same id door refused it.
4. `TOOL: problem.set_approval(id='version_option_show_python', approval='approved')`. `OK problem.set_approval -> {"id": "version_option_show_python", "approval": "approved"}`.
5. `TOOL: problem.prioritize(id='version_option_show_python', priority='high')`. `OK problem.prioritize -> {"id": "version_option_show_python", "priority": "high"}`.
6. Prose: `The item has been prioritized with a high priority.` No call. The session ended.

No door spoke at turn 5. The op `problem_prioritize`, `rota/roles/api.py:1149`, declares `priority: int` and writes `{"priority": priority}` with no check. The binder, `rota/core/sandbox.py:205-220`, checks a container where a scalar is declared and the enum table, and nothing else. The column is `priority INTEGER NOT NULL DEFAULT 0`, so SQLite's affinity turned `'1'` into 1 for s180 turn 6 and s243 turn 2, and kept `'high'` as text. The word came from the seat. The prompt's signature line is `TOOL: problem.prioritize(id, priority)` with no type, the brief says `order them with problem.prioritize`, and the relay held no number (observed: `q5.py`, the system prompt of s249 and the schema, 2026-10-06).

Walk 3 (observed: the log, the sessions and `probes/walk.py`, 2026-10-06). It started at 15:58 on the request `version_option_show_python`, m_p3, at s227. Each iteration of the walk is one `loop.step`, and an ask is pumped before the step and counted apart. It made 23 steps, s227 to s249, and 3 asks: `[m129] confirm`, `[m138] present`, `[m143] clarify`. The last wake was s249, the Vision Keeper on m145. The 24th step crashed in `frontier` before any wake: `loop.step` → `frontier` → `all_wakes` → `batch_start` → `tick_batch_start` → `next_batch`, `rota/core/scheduler.py:1382`, `TypeError: bad operand type for unary -: 'str'`. The log ends with the night counter and `launcher done 16:09 exit 0`.

Could a step run again: no. `q6.py` opens the database read-only and calls the night tree's `next_batch`. It raises the same `TypeError`. The rows it sorts are bg_1, `deferred`, priority 5, `parked` is true, and bg_3, `pending`, priority `'high'`. Every `loop.step` calls `frontier`, so every step crashes until the row changes. On a copy with the one value set to 1, `next_batch` returns bg_3 and the batch would start (observed: `q6.py`, 2026-10-06).

The end state (observed: `state.py`, 2026-10-06):

| Batch | Status | Head | Item | What it means |
|---|---|---|---|---|
| bg_1 | `deferred` | 10e3fa7c71 | `echo_json`, priority 5 | parked by `do:park` in walk 2 at attempt 11 of 10. `-|do:park|bg_1` stands at 1 attempt. A new commit on the change starts it again, as the walk's `Stuck` line says |
| bg_2 | `merged` | a0d92ad4f9 | `confirm_default_on_eof`, priority 1 | on clickI's `main` at 8628cd3, `rota: deliver bg_2`, with 1486e60, `rota: tests of bg_2` |
| bg_3 | `pending` | none | `version_option_show_python`, priority `'high'` | approved at version 4, approval_ver 4, 1 ticket and 6 criteria. It is the next batch, and its priority row is the crash |

How bg_2 started (observed: the log of walk 2, the sessions s208 to s226, 2026-10-06). Walk 1 ended `Stuck` with bg_1 `running` at attempt 11. In walk 1 the attempt cap gave `tick:exhausted` to the Developer s172, the Architect s173 and the Vision Keeper s178. The Architect's proposal m86 reached the principal through m87 and m88, and the answer came back as the relay m90 to the Vision Keeper, section 9 wall 3. Walk 2 started at 15:48. After the Liaison's confirm and present, the scheduler ran `do:park: deferred bg_1; its ladder is spent`. `next_batch` filters a parked batch, so `tick_batch_start` woke the Developer s223 on bg_2. Night 125's bg_2 and bg_3 stayed `pending` behind a running bg_1 whose key was quarantined, frame 87. Night 126's bg_1 reached the cap, the ladder ran through, and the park freed the place. The two nights differ in the cap, not in a repair: night 125 stopped at attempt 6 by the tick cap, and night 126 reached attempt 11 by the loop cap (reasoned: `parked()` in `rota/core/scheduler.py:1487`, and the two end states).

What bg_2 held (observed: `acts.py` on s223 to s226, `git show` on clickI, 2026-10-06). The Developer s223 wrote `default_on_eof: bool = False` into `confirm()` in `src/click/termui.py`, and a return of the default in the `except (KeyboardInterrupt, EOFError)` branch. Its first write, turn 3, dropped 13 lines after `raise Abort() from None`, the `code.write` result said so, and the commit 6e791d2 landed beside the note. That is frame 140's sign, 1 case. Its second write, turn 7 with `end=342`, put the lines back and committed a0d92ad4. The Tester s224 stored two tests after 5 refused encodes: `tst_confirm_eof_default`, two functions that set `sys.stdin` to `StringIO("")` and call `confirm("Are you sure?", default=True, default_on_eof=True)`, and `tst_confirm_flag_exists`, which asserts `"default_on_eof" in sig.parameters`. The harness: `34 test(s), 0 not passing`, then `36 test(s), 0 not passing`. The Critic s225 emitted `pass` with `reason=''`. The Architect s226 wrote two findings `satisfied` against `k0`, `this area has not been surveyed`. Then `do:merge: merged bg_2`.

Is the merge right of its tests: yes. 36 of 36 pass at a0d92ad4, and the merged `confirm()` on `main` is whole, with the flag, its docstring, and the lines that the first write dropped (observed: `git show 8628cd3:src/click/termui.py`, lines 288 to 358, 2026-10-06). The two reviews were thin: an empty reason and findings against a constraint that says nothing of this area (reasoned: the two sessions' calls). s223 also tried to write the Tester's file 3 times and met `the tests are the Tester's`, frame 148's door, with no call named that it could use.

## 7. The night as a whole

(observed: the log, `q8.py`, `state.py`, 2026-10-06)

| Phase | Clock | Sessions | Turns | Steps and asks | End |
|---|---|---|---|---|---|
| onboarding | 14:33 to 14:55 | s1 to s110 | 320 | 126 steps, 11 asks | `ONBOARDED`, 4 things approved |
| walk 1, `echo_json` | 14:55 to 15:48 | s111 to s207 | 566 | 121 steps, 13 asks | `Stuck: the code is written, but 4 tests are still failing` |
| walk 2, `confirm_default_on_eof` | 15:48 to 15:58 | s208 to s226 | 95 | 25 steps, 3 asks | `MERGED (1 total)`, then `Stuck: bg_1 is parked` |
| walk 3, `version_option_show_python` | 15:58 to 16:09 | s227 to s249 | 92 | 23 steps, 3 asks | the crash, section 6 |

- Sessions by role: Liaison 74, Vision Keeper 69, Terminologist 39, Architect 25, Developer 17, Critic 15, Tester 10. Developer sessions: 16 in walk 1, 1 in walk 2, 0 in walk 3.
- Commits landed: 21. 19 on bg_1 in s130, s143, s164, s165, s166, s167, s168, s171 and s182. 2 on bg_2 in s223. Harness lines: 13, 11 on bg_1 and 2 on bg_2. Heads with stored runs: 10.
- `CYCLE` lines: 0. The scheduler's quarantine: `-|tick:constraint_zero|` at 3 attempts, quarantined and reported to the Liaison s1 at the start of onboarding.
- Crashes: 1, section 6. `night126.err` holds that traceback and nothing else. 249 of 249 sessions are committed.

The chain of bg_1, in short (observed: `dev1.out`, `dev2.out`, `tst.out`, 2026-10-06). s130 committed `echo_json` as a plain function, 34 of 34 passed. The Testers s131, s134 and s137 landed 0 of 12 encodes. s139 stored three tests that pass the plain function to `CliRunner.invoke`, frame 131's first sign, 37 tests and 3 red. The Developer challenged `inh_echo_json_03` twice, m64 and m73, and the Tester s150 stored a direct call with `pytest.raises`, green at attempt 4. The Developer challenged `inh_echo_json_01` twice, m76 and m77, and the Testers s154 and s156 sent no encode, section 1. The bound then refused every later challenge on those refs, 11 times. From attempt 5 to 11 the Developer wrapped `echo_json` as a command, unwrapped it, put `import json` at module level, and at 10e3fa7c71 changed the signature to `echo_json(json_string: str)`. That broke `inh_echo_json_03` too, 4 red. The ladder ran at attempt 10, and walk 2 parked the batch.

## 8. The night counter

The counter printed at the end of the log, verbatim: `made up: 84 turns, 33 sessions (architect 2, critic 2, developer 13, terminologist 1, tester 1, vision_keeper 14)`, `ran anyway: 2 writes after an invention (2 turns with a write result), 9 with a landed commit`, `dangling pointers: 66 turns, 15 sessions ... Most such turns: s165 (13), s171 (11), s153 (7)`, `repeats: 4 wakes repeated, 10 sessions, 6 of them repeats` (observed: the log, 2026-10-06). Night 125's counter: 49 made-up turns in 23 sessions, 2 landed commits, 20 dangling-pointer turns in 6 sessions (copied: `plans/night125-read.md`, section 6).

The dangling pointers (observed: `q7.py`, `q9.py`, 2026-10-06). The counter marks a turn when its prompt holds the eviction notice and a repeat tail anywhere, so the 66 turns are a ceiling. 20 sessions hold a notice in 149 turns. 13 of them are Developer and Tester sessions of walks 1 and 2.

- **s165, attempt 5, 25 turns.** The notice stood from turn 6, 6 exchanges dropped, then 3 to 5. `asked three times` refusals: `batches.expect` at turns 14 and 23, `code.source` at turns 19 and 21. At turn 19 the exact span, `690, 715`, still stood in the prompt. At turn 21 it was gone. The seat re-read nothing that was dropped. It landed 4 commits after the first notice, 0612d256, 14495c13, e51227eb and 74a8aaef, the last the repair of the import failure.
- **s171, the answer m85, 25 turns.** Notices of 2, 11, 3 and 7 exchanges. At turns 8 and 12 the seat sent 6 `code.source` reads in one reply, and both replies were cut at the output budget. The refusals at turn 8 named spans that stood in the prompt, 5 of 5. The seat landed 3 commits after the notices, 586170a4, 02cbfb5e and a87f9290, each a wrap of `echo_json` as a command.
- **s153, attempt 4, 14 turns.** A notice of 8 exchanges from turn 6. The repeat tails are `unchanged since you asked` on `code.source`, served and not refused. The seat read 5 spans again, wrote an unchanged text once, and landed the challenge m76 at turn 12.
- Over the night, 22 `code.source` refusals of `asked three times` stood after an eviction. In 10 the exact span still stood in the prompt. In 12 it was gone: s155 turn 11, 9 copies in one reply, s159 turns 19 and 21, s165 turn 21. In those 12 the sentence `The answer is in this prompt` was false. The serve-again rule, `the earlier answer was dropped to fit the window ... ran again`, fired in s166 and s182, 2 times each, and 0 times in the three sessions above. Whether the cap of 3 serves was reached there was not read.

Repeats: not read. The 4 groups are in the counter's own output and not in this record.

## 9. Walls on this night

New walls, with no open frame (reasoned: the headings of `plans/stack.md`, read by grep):

1. **`problem.prioritize` admits a string, and `next_batch` crashes on it.** 1 write, 1 crash, and the night ended. Section 6. The op declares `int`, the binder checks containers only, and the column's affinity kept the word. A door on the type, or a cast with a refusal, is the repair. 3 earlier writes of a string, `'1'` from s180 and s243, landed as 1.
2. **The not-Python door of `tests.encode` names a wrong cause and no step.** 12 refusals in 4 Tester sessions, s134, s139, s156, s170: `the body is not Python (invalid syntax. Is this intended to be part of the string?, line 6). A test is code the harness can execute -- def test_...(): with assertions, not a description of one`. Each body is a `def test_` with assertions. The seat wrote `["{\"key\": \"value\"}"]` inside a single-quoted body, Python reads `\"` as `"`, and line 6 holds `["{"key": "value"}"]`. The line is right and the second sentence is wrong. s139 recovered at turn 3 with a double-quoted body. s156 and s170 sent the same body 2 and 3 times, and s156 lost its challenge there, section 1 (observed: `q2.py` section 5, `q4b.out`, `tst.out`, 2026-10-06).
3. **The ladder's end relays a batch id to the Vision Keeper's approve step.** m90 and m92 carry `refs: ["bg_1"]` and `principal_verdict: {"bg_1": "approve"}`. s177 sent `problem.set_approval(id='bg_1', approval='approved')` 3 times and met `'bg_1' is already a row of batches`. s180 met it 3 times, tried `msg_1`, then approved and prioritized `defines_commands_and_options`, an item the principal did not name. m145 carries a ticket id the same way, and s249 met the door twice before the write of wall 1 (observed: the prompts of s177 and s249, `acts.py`, 2026-10-06).
4. **The same-refs step says `End the session with no call.` while a challenge on another red test lands.** s169 turn 2, m84, answered by s170 as m85. 1 case. Section 2.
5. **The repeat refusal says `The answer is in this prompt` after the window dropped the answer.** 12 of 22 `code.source` refusals after an eviction, in s155, s159 and s165. Section 8. Frame 77's serve rule fired 0 times in those sessions, and its cap was not read.
6. **A seat sends one call a hundred times in one reply.** s218 turn 5, 111 `criteria.specify` lines in 32,057 characters, 51 refused as `those are cr_N's words already`. s245 turn 2, 96 lines, 5 landed and 25 refused as `six is many`. Both replies were cut. The stores hold 2 and 6 criteria, so the structure held. The runner's comments call this the s71 storm (observed: `q8.py`, the two traces, 2026-10-06).
7. **Reply cuts.** 22 `reply cut` result lines in 15 sessions from s130 on, by the result tails: 3 in s171, 4 in s230, 2 in s218 and s245. The runner's accounts list more, 3 for s156 alone, because a cut reply's tail is not always found (observed: `q8.py` and the `SESSION ENDED` accounts, 2026-10-06). Night 125's read counted no cuts, so there is no baseline.

Known walls with a case on this night:

| Frame | Cases | Evidence |
|---|---|---|
| 131, a plain function as a Click command, the product changes to fit | 19 commits on bg_1 | 3 tests of s139 pass `echo_json` to `CliRunner.invoke`. The Developer wrapped it 6 times and changed its signature at 10e3fa7c71 |
| 146, a write lands a module that fails at import | 1 | b9e515bfdf, 37 `error`, `@click.command()` with no `click` name |
| 140, a span write drops its tail and the commit lands beside the note | 1 | s223 turn 3, 13 lines dropped, 6e791d2 landed, repaired at turn 7 |
| 129, a Vision Keeper authors a decision and asserts it as a new item | 1 | `echo_json_compact_v2`, asserted by s158 and s174 from a criterion's words. It went to signoff and slicing, s183 to s203, and the Critic s196 falsified it: `The probe for def echo_json returned an empty list` |
| 148, a refusal names a call that the doors refuse | 2 | s172 turn 1, the refs door names `refs=['echo_json_compact', 'inh_echo_json_01']` and the bound refuses it. s223 turns 14 to 16, the test-file door names `msg.challenge_tester` on a batch with no red test |
| 115, the Architect's answer carries no words | 2 | m83 and m93, `body_text` is null |
| 116, one challenge per red test in one reply | 1 session | s140 turns 5 to 7, 3 challenges and an escalation in one reply, 3 times |
| 154 item 6, `they answered (answered)` | 5 | the escalation door in s166 and s167 |
| 137, a parser refusal names a wrong thing | 7 | section 4, `invalid syntax (<unknown>, line 1)` 5, `never closes` 2 |
| 113, made-up tool results | 84 turns, 33 sessions | the counter. 9 landed commits in such sessions |
| 130, the fix wake and a red project test | 6 heads | `test_light_imports` red from attempt 6 to 11. s171 turn 13's write result named it. No Developer changed the import |

Known walls with 0 cases: frame 87, bg_1 was parked and bg_2 started. Frame 149 and 161, 0 reverts. Frame 150, 0 commits refused by a door. Frame 151, 155 and 156, 0 wrong reads. Frame 142, 0 park asks. Frame 159 and 160, 0 owed-call nudges for a Developer. Frame 147, 5 constant-assertion refusals in s131, s141 and s150, each on a body whose only assertion is `assert False` or `assert True` inside a `try`, and s150 landed `pytest.raises` at turn 7, so the door's sign of a right test refused is 0 (reasoned: the bodies in `q4b.out` and `tst.out`).

## 10. What this read did not read

- The turns of s1 to s129, except the refusals by first words in `q8.py`.
- The turns of walk 1 after s182, except s196, s218 and the sessions named in section 9. The `echo_json_compact_v2` chain is from the rows.
- The repeat groups of the counter.
- Frame 77's serve cap against the 12 false `in this prompt` sentences.
- The full prompts of the Developer sessions. The read used the replies and the result parts.
- No test body was run. Every verdict on a body is reasoned.
- The design records of frames 144, 149, 151, 152 and 153. The baselines are copies from the brief and from `plans/night125-read.md`.

Status 2026-10-06 16:25: written by an agent of session 488d31af from the final database. Not committed. Rota workflow, except section 5, which is about the meta workflow's tier.
