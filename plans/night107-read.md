# Night 107, the read

Night 107 ran from a worktree at 8925d78, launched 2026-10-02 15:52, ended 17:49 with `launcher done 17:49 exit 0`. It is the walk of frame 110. NIGHTCOUNT: 213 sessions, 910 turns; made up 64 turns in 34 sessions, developer 9; ran anyway 0 writes after an invention, 1 with a landed commit (0e6500a4); dangling pointers 66 turns, 12 sessions; repeats 4 wakes, 16 sessions. Read on Opus from `.rota/night107_report.txt` (149 lines), `.rota/night107.log` (113 lines) and 24 read-only queries on `.rota/clickI_night107.db`. Every statement is about the rota workflow and is (observed: query, 2026-10-02) unless it carries another mark.

## 1. Frame 110, the challenge push

No challenge named a test that crashed before its assertion. Five challenges landed, and two of them carried a failed test. The new plain-text block reached both of those Tester seats.

| Challenge | Test, last run | Tester | Plain block | `code.source` | `tests.encode` | After |
|---|---|---|---|---|---|---|
| m55 | `tst_echo_json_compact_6`, failed at its assert, line 14 | `s137` | yes | no | 1 refused (file clash), 1 landed, v3 | pass at 6037f989 and 956f4e5a |
| m56 | `_2`, passing | `s139` | no | yes, `utils.py` 0-400, 688-732 | none | answer m57, defended |
| m58 | `_4`, passing | `s143` | no | no | 1 landed, v3 | pass at 956f4e5a |
| m61 | `_3`, labelled "failed before any assertion" | `s151` | yes | no | 6 calls, 3 refusals shown, none landed, stays v1 | fails again at 956f4e5a, same line 11 |
| m64 | `_4`, passing | `s155` | no | no | 2 refused, "the body is not Python" | no reply, see section 2 |

- `s137` user text opens with `[last run of tst_echo_json_compact_6: failed]`, then "The test's body:" and "The failure output:". The `output_tail` first line is `F ... [100%]`.
- `s151` user text opens with `[last run of tst_echo_json_compact_3: failed before any assertion]`. The `output_tail` first line is `_ _ _ _ _ _ _`. The label is wrong: the output ends at the test's own `assert "TypeError" in str(e)`, `test_echo_json_non_serializable.py:11: AssertionError`. The chained `TypeError` from `json/encoder.py:182` sits above it.
- `s151` refusals: "every assertion here is on a constant", then twice "the test chooses 'lambda' ... That is an assumption". It then answered m62 and was refused a second answer.
- One test rose in version and went green: `tst_echo_json_compact_6`, v3, written by `s137`, pass at attempt 6 on 6037f989. The fault was in the test, `.strip()` against an expected `"\n"`.
- No Tester called `code.source` on a challenged failing test. The only Tester `code.source` call was in `s139`, on a passing test.
- Three of five challenges named a passing test: m56, m58, m64. A Tester woken on a passing test gets no plain block, by design (reasoned: the block prints failed runs only).

## 2. Frame 111, the baseline

- "on exactly these refs already" refusals: 6, in 2 sessions, `s153` 3 and `s157` 3 (counted as the most such lines in one prompt). Other challenge refusals: "you have already sent challenge to tester" in `s136`, `s142`, `s150`, `s153`, and "'echo_json_compact_1' names no row" once in `s153`.
- `msg.escalate_architect` landed twice. m63 from `s153` and m66 from `s157`, both with `body_refs` `["echo_json_compact_3", "tst_echo_json_compact_3"]` and an empty `body_text`. Each sender had one more escalate refused, "you have already sent escalate to architect".
- m63 went to `s154`. The Architect sent no answer. It sent m65, a challenge to the Vision Keeper, refs `["echo_json_compact_3"]`, `body_text` the criterion text. `s156` then authored decision `d_771967ccf5` and re-asserted `echo_json_compact_3`.
- m66 went to `s158`. The Architect sent nothing: its last call is `model.load`. Both escalations still read `status = answered`.
- The one Architect answer to the Developer is m67, from `s159`, a `tick:unresolved` on m64. Its `body_refs` is `["echo_json_compact_4"]` and its `body_text` is empty. `s160` read it in one turn and changed nothing.
- `code.write` refusals with "monkeypatch shielding": 0. No refusal line names monkeypatch. No batch test `tst_*` body holds `sys.stdin`. The echo_json batch does not reach the stdin door.

## 3. Frame 112, repeated Developer wakes

Developer `tick:tests_failing` wakes on `echo_json_group` ran at attempts 3, 4, 5, 6, 6, 7, 8, 8, 8, 9, 9, 9. Three sets share an attempt detail.

| Attempt | Sessions | Head | Between them | Pure repeat |
|---|---|---|---|---|
| 6 | `s138`, `s141` | 6037f989 | m56, m57 (`s139`, `s140`) | no |
| 8 | `s144`, `s145`, `s146` | 956f4e5a | nothing, no commit | yes |
| 9 | `s150`, `s153`, `s157` | 956f4e5a | m61 to m66 | no |

Pure repeat groups: 1, of size 3. This matches the log's `CYCLE: period 1, rounds 3, wakes: developer|tick:tests_failing|attempt 8|["echo_json_group"]`. The report counts 4 repeated wakes in 16 sessions, which includes the two sets with messages between.

## 4. Frame 113, made up

Completions that hold their own `OK` or `ERROR` result line: vision_keeper 20 turns in 11 sessions, architect 10 in 4, critic 4 in 4, terminologist 3 in 3, tester 2 in 2, liaison 1 in 1, developer 24 in 9. Total 64 turns, 34 sessions, the same as the report. Developer tools: `code.source` 33, `msg.challenge_tester` 4, `msg.escalate_architect` 3, `tests.load` 3, `code.write` 2, `code.commit` 2, `criteria.load` 1.

Two sessions with a landed commit also hold an invented `code.commit` line: `s127` (71d3a052, 0e6500a4) and `s135` (081abfb5, 6037f989). In both, the line copies the real result that sits in the same turn's prompt: `s127` seq 21 and `s135` seq 14. The report flags only 0e6500a4, because it does not parse the `committed: True` form (see section 7).

## 5. Frame 114, inherited tests

Yes. At 6037f989, 25 tests failed, and all 25 are inherited (`inh_*`, no `criterion_id`). At 956f4e5a, 26 failed: the same 25 and `tst_echo_json_compact_3`.

- 6037f989 is `s135`'s second whole-file rewrite of `src/click/__init__.py` (`start=0, end=-1`, 2289 bytes). Its first, 081abfb5 at 2248 bytes, has no test run. The errors are `AttributeError: command`, `group`, `style`, `INT`, `Argument`.
- Earlier, at 29b78708 (`s134`, `__getattr__` edit), one inherited test failed: `inh_86bace6b`, `test_deprecations.py`.
- No later commit touched `src/click/__init__.py`. `s138` tried, and the door refused: "this write changes __getattr__, and no criterion of this batch names it ... The project's own tests call __getattr__ as it is".
- The batch stays `running` at 956f4e5a with 26 red. Walks 2 and 3 end "Stuck. The team gave up on: tests_failing for echo_json_group".

## 6. The stall

`echo_json_group` was given up, not parked. The tick key `developer|tick:tests_failing|echo_json_group` reads `attempts=3 quarantined=1 reported=1`, while the wake details reach attempt 9. The log holds one CYCLE line, quoted in section 3, and no `do:park` line. Liaison `s147` and `s161` reported "1 abandoned: tests_failing for echo_json_group (developer), 3 attempts".

- `echo_json_group`: 6 commits, 0 merges. `s127` 71d3a052, 0e6500a4; `s134` 29b78708; `s135` 081abfb5, 6037f989; `s141` 956f4e5a. The report prints 3.
- `echo_json_group_new` (confirm_default_on_eof) and `echo_json_group_v2` (version_option_show_python): grouping, annotation and approval only, `pending`, 0 commits.
- NIGHTCOUNT clickI: 213 sessions, 910 turns.

## 7. New, held by no frame

- The report's commit column misses the `committed: True, head_commit: ...` form: `s134` and `s135` show "no commit line", and the batch shows `commits=3` against 6 landed (`night107_report.txt` lines 3-7).
- The write door let a whole-file rewrite of `src/click/__init__.py` drop the package exports. The "drops ..." guard fired on `utils.py` rewrites (`s127`, `s142`) only (`s135` seq 6 and 14).
- The failure label "failed before any assertion" fires on a test that reached its own assert, when a chained exception sits above it (`s151` seq 1).
- The Developer challenged three tests whose last run passed: m56, m58, m64 (`s138`, `s142`, `s153`).
- The `__getattr__` door blocks a repair of a file that a batch commit already broke (`s138`).
- The made-up counter counts a completion that copies a real result line from its own prompt (`s127` seq 21, `s135` seq 14).
- An escalation with no reply still reads `answered` (m66, `s158`).
- The Architect named the second and third batches after the first: `echo_json_group_new`, `echo_json_group_v2` (`s184`, `s205`).
