# Dry run 6c: why the Tester's tests do not land, the read of the door refusals, 2026-11-06

## Result

Two doors refuse good tests on every project. Together they make 30 of the 102 door refusals in dry runs 3 to 6c. The rest are true refusals, and most of those come from words that rota itself gave the model.

- **The prints door is wrong on a library.** It counts "output" and "writes" as print words (observed: `PRINTS`, `rota/roles/api.py` line 9119). "The serialized output" of `to_ical` and "When icalendar writes a long line" describe a return value, and the door refused 18 return-value tests on dry runs 4, 5 and 6c (observed: `pairs.json`).
- **The collect door is wrong on two pytest forms.** It refuses any body with no `assert` statement (observed: `api.py` lines 11331 to 11340). pytest collects a `with pytest.raises(...)` test and a `unittest.TestCase` class. The door refused 9 bodies of the first form on dry run 3 and 3 of the second on dry run 6c, 12 of 12 wrongly (observed: `ast` read of the 12 bodies, `pairs.json`).
- **On dry run 6c, the criterion that parked the batch is `c_3`, and no `c_3` try was refused for a backslash.** The `c_3` tries met these refusals: the path clash twice, with good bodies, on turns that ended the session. They also met the prints door once, an import of `billing` copied from the prompt's example, a "tombstone" test copied from the prompt's glossary example, and `fold`, a name that does not exist (observed: `pairs.json`, s178 to s183).
- **The path clash is right, and its hint is wrong for a package layout.** One stored test is one file, so two tests on one path overwrite each other. The hint says `tests/test_<what it checks>.py`, a root folder that icalendar does not have (observed: `api.py` line 12719, the icalendar `pyproject.toml` `testpaths`).
- **The retired `c_2` reached the Tester through the wake.** The Terminologist retired `c_2` and then answered the Tester with `refs=['c_2']`. The wake showed the text of `c_2` and "principal_verdict: contest", and gave no sign that `c_2` was retired (observed: s191 `tool_calls`, s192 turn 1 `user`).
- **The block form `body=[body]` is used by no recorded Tester call.** No prompt names it. 0 of 3,263 register completions with `tests.encode` use it, and 0 calls on the dry runs use it (observed: `block.py`).

The scripts and their output are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/tests_read/`: `catalog.py`, `pairs.py` (it writes `pairs.json`), `block.py` and `rank.txt`. Every database was opened with `immutable=1`. A database's `-wal` file was 0 bytes for dry runs 3, 4, 5 and 6b, so `immutable=1` lost no rows (observed: `ls -la`). Dry runs 6 and 6b turns 1 to 4 had no Tester session (observed: `dry6-read-2026-11-06.md` count 3, `sessions` of `dry6b.db`).

How to read the counts. One row is one `tests.encode` call of a Tester session, paired with its result line in the next turn, or with the runner's account for a last turn. "Door" means the call was read and a door of `tests_encode` refused it. "Parser" means the recorded result is a call-parser `ToolError`, which this read leaves out, as the brief says. The cause is the class of the refusal text. The next act is the same session's next turn (reasoned: the pairing is by order inside a turn, and a last turn's refusals are matched by the stored `tests` rows).

## 1. The refusals that reached the door

### Dry run 6c, 52 Tester encodes: 1 landed, 11 parser, 2 not run (a verbatim repeat), 38 door

| Cause | Refusal, verbatim | Count | Sessions | Next act |
|---|---|---|---|---|
| Import of a name the module lacks | "src/icalendar/parser/string.py does not define fold, and no criterion names it: this test imports a name the module does not have, and the harness dies at collection. Import only what the module defines, or the surface the criterion names" (9). The same text for `vEvent` in `src/icalendar/prop/__init__.py` (2). "src/icalendar/__init__.py does not define to_ical, and this test imports it from there; the harness dies at collection. Nothing in the tree defines it yet; the Developer writes it first" (1) | 12 | s174, s178, s182, s183, s186 | changed 5, same 2, another criterion 1, a question or a triage 3, session ended 1 |
| The surface is never called | "this test never calls 'to_ical', the surface the criterion names -- call it and assert on what it returns or does. ..." | 6 | s181, s182 | changed 2, same 2, session ended 2 |
| The prints door | "the test uses what to_ical returns, and the criterion, its ticket or the principal's words say it prints; nothing says it returns anything. That is an assumption, and it is logged where it is made: ledger.log(...) -- then send this encode again unchanged. Or assert on what it prints" (1). "the test uses what to_ical returns, and the criterion c_2 says it prints" (1) | 2 | s181 | changed 1, session ended 1 |
| No such module | "this test imports billing, and no module of that name exists in the tree: the import path is the worktree root and src/, and the modules there are generate_windows_to_olson_mapping, icalendar, news, src. If the surface has no module yet, the Developer writes it first" | 4 | s178 | same 2, a triage 2 |
| The path clash | "src/icalendar/tests/test_folding.py is already c_1_fold's file; two tests in one file overwrite each other on disk. Name this one for its own criterion -- tests/test_<what it checks>.py" | 3 | s180, s181 | session ended 3 |
| The collect door | "pytest will collect nothing from this body: it needs a def test_...() containing at least one assert. A sentence about the criterion is the criterion again, not a test of it" | 3 | s177 | changed 1, same 2 |
| Not Python | "the body is not Python (unexpected character after line continuation character, line 13)" (2), "line 10" (2), "line 1" (2). "A test is code the harness can execute -- def test_...(): with assertions, not a description of one" | 6 | s182 (4, the model's text), s186 (2, the parser's misread, fixed at `566b945d`) | changed 3, same 3 |
| Retired criterion | "c_2 is retired: the principal's ruling r_m54 dropped its line. Encode only the live criteria of the batch" | 2 | s192 | `tests.retire` 1, a question to the Vision Keeper 1 |

(observed: `pairs.json`, `texts.txt`.)

### Dry runs 3 to 5, 116 Tester encodes: 39 landed, 2 parser, 1 not run, 2 empty results, 64 door

| Cause | Refusal, verbatim (shortest form) | Count by run | Next act |
|---|---|---|---|
| The prints door | "the test uses what q_split returns, and the criterion c_1 says it prints: `q_split` is a plain function in `src/icalendar/parser/parameter.py`" and the long form with `ledger.log` | dry4 7, dry5 9 | changed 9, same 4, a question or a triage 2, session ended 1 |
| The collect door | the text above | dry3 9 | changed 9 |
| The program-file path rule | "path 'src/icalendar/tests/test_icalendar.py' is a program file of the project. ... Write the test in a test folder of the index: .github/workflows. For example, path='.github/workflows/test_test_icalendar.py'" | dry4 4, dry5 3 | same 6, changed 1 |
| Import from another module | "the surface 'src/icalendar/parser/parameter.py::q_split' lives in parameter.py and this test imports from icalendar.parser.string. Import the surface from its own module: `from icalendar.parser.parameter import q_split`" | dry4 3, dry5 4 | same 3, changed 2, a read 2 |
| Import of a name the module lacks | "src/icalendar/parser/parameter.py does not define _foldline, and no criterion names it: ..." | dry4 2, dry5 3 | changed 1, a read 2, a question 1, session ended 1 |
| Triage first | "c_1 has no triage verdict from you yet. Call tests.triage(criterion_id='c_1', verdict='encodable') and then tests.encode in the same reply. ..." | dry3 3, dry5 3 | the encode again with the triage, 6 |
| The replace rule | "tst_fold_c1 is stored at src/icalendar/tests/test_fold_max_length.py. To replace it, send this encode again with path='src/icalendar/tests/test_fold_max_length.py'." | dry4 4 | same 2, `tests.retire` 1, session ended 1 |
| Not Python | "the body is not Python (invalid syntax. Is this intended to be part of the string?, line 5). ..." | dry4 3 | changed 1, same 1, a triage 1 |
| The path clash | "tests/test_caselessdict.py is already tst_c2_no_dup_keys's file; two tests in one file overwrite each other on disk. ..." | dry3 2 | changed 2, both landed at a new path |
| Constant assertion | "every assertion here is on a constant, so the test checks nothing and would report as coverage. ..." | dry3 2 | changed 1, a question 1 |
| Triaged cannot | "c4 was triaged cannot in this session. A routed criterion gets no test. ..." | dry4 2 | another criterion 2 |
| The surface is never called | "this test never calls 'src/icalendar/parser/parameter.py::q_split', ..." | dry4 1 | changed 1 |

(observed: `pairs.json`, `texts.txt`.)

## 2. Was the door right

| Cause | Door right? | The refusal mends? | Example |
|---|---|---|---|
| The prints door | **No.** "output" and "writes" are print words in `PRINTS`. A library's serialized output is a return value | It steers to `ledger.log` or capsys, a wrong mend | s181 t1, `tst_c3_fold`: it calls `cal.to_ical()` and asserts on the decoded lines. Refused because the item says "When icalendar writes a long line" (observed: `api.py` lines 12417 to 12446, the item text) |
| The collect door | **No**, 12 of 12 | It says "pytest will collect nothing", which is false | dry3 s183 t1: `def test_...():` with `with pytest.raises(ValueError):` and no `assert`. 6c s177 t2: a `unittest.TestCase` class with `self.assertFalse` (observed: `ast` read) |
| Import of a name the module lacks | Yes. The import fails at collection | Partly. It does not name what the module defines. The `to_ical` text is false: "Nothing in the tree defines it yet". `to_ical` is a method of `Component` | s174 t1, `from icalendar.parser.string import fold`. The module defines `_foldline` (observed: `string.py` line 119). s182, `from icalendar import to_ical` |
| The surface is never called | Yes, in the 6 cases of 6c | Yes | s182 t4, `str(cal)` in place of `to_ical()`. s181 t1, `comp.tombstone()` |
| No such module | Yes | Yes. The cause is the prompt | s178 t1, `from billing import prorate`, the example of `tester/tests_missing.md` lines 39 to 42 (observed) |
| The path clash | Yes. A stored test is a whole file | The hint names a root `tests/` folder, wrong for a package layout | s180 t1: `c_1_fold`, `c_2` and `c_3` in one reply, all at `src/icalendar/tests/test_folding.py`. `c_1_fold` landed, and the other two were refused |
| The program-file path rule | Yes on `test_icalendar.py`, an existing test file of 100s of tests. Its hint `.github/workflows` was wrong | No | dry5 s208 t2. Fixed by `bb46c4e9`, 2026-11-04, frame 362 pass 5b (observed: commit body) |
| The replace rule with the program-file rule | The two doors contradict | No: each names the path the other refuses | dry4 s226 t14 to t19: "send this encode again with path='src/icalendar/tests/test_fold_max_length.py'", then t15 refused that path as a program file (observed) |
| Import from another module | Yes, against a wrong surface. The guess `q_split` was wrong (dry run 5 wall 7) | Yes for its rule | dry5 s219 t3, `from icalendar.parser.string import _foldline`. That is the right function, and the criterion named `q_split` |
| Not Python | Yes for s182 and dry4. s186 was the parser's misread | No: frame 166 | s182 t3, `"Test Event with \\"escaped\\\"` (the wall 5 read) |
| Retired criterion | Yes | Yes, but the wake had asked for `c_2` | s192 t1 |
| Triage first, triaged cannot, constant assertion | Yes | Yes | dry3 s181 t1 to t3 |

## 3. The provenance

The first commit of each refusal text (observed: `git log -S --reverse` on `rota/roles/api.py`, and the commit bodies).

| Cause | Commit, date, frame | Case it was built on | Ruled or reasoned |
|---|---|---|---|
| The prints door | `8234b716`, 2026-09-13. `af2f83f8`, 2026-09-14, wake audit finding 34. Narrowed by frame 321 (`plans/archive/stack-2026-10-26.md`) | clickI night 28: `echo_json` printed and returned `None`. A CLI | Reasoned by a session. `rota/DECISIONS.md` line 957 keeps "whether 'display' means return or print is a judgement" outside the doors. The word list puts "output" and "writes" inside one |
| The collect door | `bfd149d1`, 2026-09-01. The second text came with `38b751d4`, 2026-11-04, frame 362 | S0: a test written as an English sentence | Reasoned. `DECISIONS.md` lines 948 to 958 list the certain facts the doors check. "No assert" is not among them |
| Import of a name the module lacks | `aa23868a`, 2026-09-12 (no such module). `2ceef0c4`, 2026-09-13 (the "Nothing in the tree defines it yet" text). `a113c834`, 2026-09-14 (any name) | clickI night 24 `from echo import echo_json`, tipsAY `from split_bill import split_bill`, click night 55 `_sentinel` | Reasoned, from measured loops |
| The surface is never called | `0a6285ed`, 2026-09-03 | the S0 walk: a test mocked the builtin and never called the function | Reasoned |
| The path clash | `e8c68bec`, 2026-09-02, S0 walk twelve | two tests on one path overwrite each other | Reasoned. It is listed in `DECISIONS.md` line 951 as a certain fact |
| The program-file path rule | `5ae7f5f5`, 2026-10-26, frame 328. The hint order is from `bb46c4e9`, 2026-11-04 | night 167 wrote the test over `src/click/utils.py` 15 times | Reasoned |
| Retired criterion | `e913db7e`, 2026-10-24, frame 306 pass 1c | a retired criterion still showed in `criteria.load` | The retire is Roman's ruling of frame 306. The door text is reasoned |
| The quarantine cap | `tick_attempt_cap` = 3 (`rota/core/config.py` line 127), law 4 | | Law 4 |

## 4. The retired `c_2`

The retire landed before the Tester's wake, and the wake carried `c_2` as its subject (observed).

1. In turn 8, Roman answered m53 with m55: "Line 4 is not what I asked. Remove it. ..." (observed: `config` `entry:m55`).
2. The Liaison s190 relayed m56 to the Terminologist with `refs=['c_2']`. The Terminologist s191 called `criteria.retire(id='c_2')`, then `msg.answer_tester(refs=['c_2'])` (observed: `tool_calls`).
3. The Tester s192 woke on m57. The wake showed `"refs": ["c_2"]`, `"principal_verdict": {"c_2": "contest"}`, the whole of m55 as `principal_said`, and `resolved_refs` with the text of `c_2` (observed: s192 turn 1 `user`). `_resolve_refs` reads `criteria` as `id, ticket_id, text`, with no `retired_by` (observed: `rota/core/runner.py` line 2864 and after). `chain_verdict` carries the contest on the cause chain with no check of the retire (observed: `runner.py` lines 2196 to 2221). `e913db7e` filtered the relay contest block and not this answer wake (reasoned: its body lists the readers it filtered).
4. The Tester was asked to cover `c_2`. It wrote a `c_2` test at `src/icalendar/tests/test_parsing.py` that names "issue #1501" and the escape branch of `_foldline`, which are the words of line 5 of m55, about `c_3` (observed: s192 turn 1 completion). Its `criteria.load` in the same reply showed `c_1` and `c_3` only. The door refused `c_2` as retired.
5. s192 asked the Vision Keeper (m58) what "retired" means. The answer m59 carried `refs=['c_2', ...]` again, so s194 tried `c_2` again (observed: m58, s194 turn 1 `user`).

So the live criterion `c_3` was never the subject of a wake after turn 7 (reasoned: the wakes of s192 and s194 name `c_2` only).

## 5. The path clash

What clashed: the path of a test already stored or staged in the same reply (observed: `api.py` lines 12710 to 12720). In s180 the model put three tests in one file in one reply, which is normal Python practice. The first was staged and the next two were refused. In s181 t2 the clash was with the stored `c_1_fold`.

What the door expects: one test per file, and a new file name. Its hint is a constant, `tests/test_<what it checks>.py`, and the prompts teach the same root path (observed: `tester/answer.md` line 13, `tester/tests_missing.md` line 37). On icalendar, the tests live in `src/icalendar/tests`, and `pyproject.toml` sets `testpaths = ["src/icalendar/tests"]` (observed). The branch above it for a project test file already names a file "beside it" with the `beside` path (observed: `api.py` lines 12688 to 12696). The plain clash branch does not.

The path clash cost `c_3` its two best bodies on 6c. s180's `c_3_escape_preserved` and s181's `tst_c3_escape` call `to_ical()` and assert on the lines. Both turns ended the session, so no repair turn came (observed: the next turn is "SESSION ENDED"). `ROTA_ONESHOT=1` ends a session at the first turn that writes or sends (the dry6c read, `runner.py` line 6327). On dry run 3, with no such end, both clash refusals were repaired in the next turn and landed (observed: dry3 s181 t3, s183 t3).

## 6. The chain from the refusals to the parked batch

| Step | Row | Rule |
|---|---|---|
| 1. s174 (turn 7) wakes on `tick:tests_missing`, "without a test: c_1, c_2, c_3". 4 turns, 0 landed | `tick_attempts` `tester\|tick:tests_missing\|b_1` = 1 | `note_dispatch`, `rota/core/scheduler.py` lines 2878 to 2896 |
| 2. s178, same wake. 0 landed (`fold`, `billing`) | = 2 | the same |
| 3. s180 on m50 lands `c_1_fold` | the count is reset | "A moved test of the batch resets it", `rota/core/db.py` lines 1159 to 1167 (reasoned: 5 tick sessions and a count of 3) |
| 4. s181, s182, s183, "without a test: c_2, c_3". 0 landed | = 3 | the same |
| 5. The wake is still ready at the cap | `quarantined = 1` | `quarantine_stalled`, `scheduler.py` lines 3101 to 3150, cap 3, law 4 |
| 6. s187 `tick:quarantined`, "1 abandoned: tests_missing for b_1 (tester), 3 attempts". m53 "The team stopped work" | `reported = 1` | |
| 7. `-\|do:park\|b_1` and s188 `tick:park_ask`, "b_1 is parked" | `batches.status = 'deferred'` | |
| 8. Turn 8: `c_2` retired. s192 and s194 land nothing. No row moves, so no reset and no lift | quarantine stays | `_lift_quarantines` lifts only on a moved red (`db.py` lines 1170 to 1183) |
| 9. Turn 9: 0 sessions | | |

(observed: `sessions`, `tick_attempts`, `batches` of `dry6b.db`.)

The last refusals before the cap were s183's. Turn 3 refused `c_2` and `c_3` for `fold`, and turns 1 and 2 were parser refusals (observed: `pairs.json`).

## 7. The source text channel

No prompt line speaks of backslashes or of escaping (observed: grep of `rota/roles/prompts/`). Each line below is a refusal, and each speaks of the form of a value.

| Site | Words | Claim against `parse_args` after `566b945d` |
|---|---|---|
| `rota/llm/toolproto.py` lines 1441 to 1448, frame 266 | "put the whole value between three single quotes at each end, with no backslashes" | False for source with a backslash. A triple-quoted value is a non-raw literal: `\n` becomes a line break and `\\` becomes one backslash (the wall 5 read, `probe194.py`) |
| `toolproto.py` lines 1453 to 1463, frame 122 | "Write the value as it is, with no backslashes: {key}='''the text, with its quotes and line breaks as they are'''" | False, as above |
| `toolproto.py` lines 1472 to 1478 | "put it between triple quotes, text='''...''', with the lines as they are, no escaping" | False, as above |
| `toolproto.py` lines 1537 to 1547 | "Put the value of {stray} between triple quotes ... with no backslashes ... No escaping, and no placeholder" | False, as above |
| `toolproto.py` lines 1551 to 1557 | "open {longest} with three single quotes, write every line of the value as it is ... No escaping" | False, as above |
| `rota/roles/api.py` lines 28389 to 28393 (`code.write`) | "Put the text between triple quotes, text='''...''', with the lines as the source has them, no escaping." | False for a backslash, as above |
| `api.py` lines 22517 to 22562, frame 335 | "Write each backslash as `chr(92)` ..." and "No form of this string with a backslash comes through the call unchanged. Write the value with no backslash." | `_call_keeps` tests forms through the live `parse_args`, so the advice follows the parser. The last sentence is false whenever a doubled backslash comes through, which it does after `566b945d` (reasoned: the code, and the wall 5 probe) |
| `tester/tests_missing.md` lines 36 to 42 | the one example body: a single-quoted value with raw line breaks | It holds no backslash. It is the form the models copy (observed: 0 block calls) |

The block form `key=[key]` is defined by `_inline_blocks`, `toolproto.py` lines 1056 to 1075, from `858d7634`, 2026-08-26 (the wall 5 read). The call line ends with `body=[body]`, and the raw lines follow up to the next `TOOL:` line. The model learns the shape only from the `[text]` blocks of the read results (observed: `runner.py` line 1994).

- Use: 0 Tester calls with `body=[body]` on dry runs 3 to 6c, and 0 in 3,263 register completions with `tests.encode`. In the register, 19 completions use `text=[text]`, all `code.write`. 10 of the 19 put `)` right after the label, a shape the docstring says the parser does not take (observed: `block.py`, SQL on `tests/rota/cassettes.db`).
- Landed share: with the block form, no case. Without it, 40 of 161 Tester encodes landed on dry runs 3 to 6c, 25 % (observed: `pairs.json`).

Proposed words:

1. In `tester/tests_missing.md`, `tester/answer.md` and the Developer's write brief, add: "A body that holds quotes or backslashes goes as a block. End the call line with `body=[body]`. Then write the lines of the test as they are, up to the next `TOOL:` line."
2. In the eight refusal texts above, replace "with no backslashes" and "No escaping" with: "Inside quotes, write each backslash of the source twice. Or send the value as a block: end the call line with `{key}=[{key}]`, then the lines as they are."

The measurement:

- Replay the first prompt of each 6c Tester session, s174, s177, s178, s180 to s183, s186, s192 and s194, with the new words. Run each 5 times on qwen3.5:9b at temperature 0, with each run on a new load, because Ollama's determinism is per load.
- Count the calls that use the block form. Count the calls whose body reaches the door equal to the meant source, against 25 of 42 today.
- Then run the register's 25 backslash cases of the wall 5 sample the same way.

The words work when at least half the backslash bodies use the block form and none of them is misread (reasoned: a threshold, not measured). The cassettes whose prompt holds the changed text go stale and are recorded again.

## 8. The match against the open frames, and the rank

The rank is by the tests lost (observed: `rank.txt`). On dry runs 3 to 6c, four criteria ended with no test: dry4 `c4` and `c7` (triaged `cannot`), and 6c `c_2` (later retired) and `c_3`. A cause's tests lost are those criteria plus the good bodies it refused.

| Rank | Cause | Reach, refusals and sessions over the runs | Door wrong | Open frame |
|---|---|---|---|---|
| 1 | The prints door | 18 refusals, 4 sessions, dry4, dry5 and 6c. On the trail of dry4 `c4`, 6c `c_2` and `c_3` | 18 of 18 on a library surface (reasoned: `q_split` and `to_ical` return values) | **None.** Frame 321 is closed. New |
| 2 | The path family: clash, program file, replace | 5, 7 and 4 refusals. It took 6c `c_3`'s two good bodies. It made the dry4 s226 loop of 6 turns | The hints: `tests/` in all 5, `.github/workflows` in 7 (fixed), a contradiction in 4 | Frame 148 (three refusals name a call that the doors then refuse) and frame 194 (two write doors contradict) are the class. Frame 128 is near. The root `tests/` hint is new |
| 3 | The collect door | 12 refusals, 2 sessions, dry3 and 6c. All 12 dry3 bodies landed later, after the model added an `assert` | 12 of 12 | Frame 147 (the constant-assertion door refuses a test that fails when no exception comes) is the same class. The collect door is new |
| 4 | Prompt examples copied | `billing` 4 refusals (s178). "tombstone" tests in s178, s181 and s182, 9 of their calls | Right, and the words came from rota's prompts | Frame 214 (the Liaison copies the converse brief's example) is the class, on another seat. New for the Tester |
| 5 | Import of a name the module lacks | 17 refusals, 8 sessions | Right on the import. The `to_ical` text is false, 1 refusal | Frame 262 (a surface the index does not hold), because `surface_refs` holds the bare method name `to_ical`. Frame 216 is the invented-import door |
| 6 | Import from another module | 7, dry4 and dry5 | Right, against a wrong guess | Frame 141 |
| 7 | Not Python | 9 (2 made by the parser) | Right, with a wrong cause | Frame 166. Frame 155 for the parser |
| 8 | Retired criterion in the wake | 2 refusals, and 2 answer sessions spent | Right. The wake was wrong | New |
| 9 | The session ends at the refused turn (`ROTA_ONESHOT=1`) | 6c: 3 of 3 clashes and 6 other refusals had no next turn | not a door | A dry-run setting. New |

`plans/wall-guide.md` has no line on the prints door, the collect door, the test path or a retired criterion (observed: grep).

## 9. Reading

1. The biggest loss is the doors that judge a test's meaning with a fixed list. The prints door and the collect door refused 30 tests, and none of the 30 was wrong (reasoned: sections 2 and 8).
2. Rule 1, for every project: a door refuses only what fails mechanically, an import, a collection or a run. A doubt about meaning is logged and does not refuse. Each door's claim is checked against the runner it names.
3. Rule 2, for every project: a refusal or a prompt that names a path or a form shows one from this project, made from the index or the wake. Never show a fixed example such as `tests/`, `billing` or "tombstoned".
4. Two smaller rules follow from the 6c chain. A wake does not carry a retired row as its subject. A turn that ends a session on a refusal gets one more turn.
5. A fix of the backslash channel alone would not have landed `c_3` on 6c. Rules 1 and 2 would have let s180's or s181's `c_3` body land (reasoned: both were refused only on the path clash, and s181 t1 only on the prints door).

## 10. What is unproven

- Whether the `c_3` bodies of s180 and s181 would pass or fail against the change. The read checked only that a door refused them.
- The count reset at s180 is read from the code and the counts, and not from a log row.
- The pairing of a last turn's refusals to its calls uses the stored `tests` rows. Where no row matched, the order of the calls was used.
- "Door wrong" for the prints door rests on the item and criterion words and on what `to_ical` and `q_split` return. No run of those tests was made.
- The block-form proposal is not measured. No model ran.

## 11. Usage

About 125k tokens. The repository changed by this page only. Every database was opened with `immutable=1`. No model, suite, gate or rota run ran. The icalendar repository at `D:/repos/_AI/sample_repos/icalendarI` was read only.
