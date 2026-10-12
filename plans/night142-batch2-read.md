# Night 142, `batch_2`: the fixed-version test that survived ten attempts

This read covers the rota workflow throughout. Sources: the copy
`.rota/clickI_night142.db`, opened read-only, the principal's file
`.rota/clickI_night142.principal.jsonl`, and the tree at 6a80be2c. Read on
Opus, 2026-10-12. The query scripts are `b2q1.py` to `b2q12.py` in the
holding session's scratchpad.

**The result: the fixed list survived because of a door, not because of
the Tester.** The only Tester prompt that carried `3.14.2` was s492. That
wake dropped the list on `tst_1` and read `sys.version_info`. The
Developer challenged `tst_2` version 6 twice, at s491 and at s493. The
challenge cap refused both times, because it counted m331, m332 and m333.
Those three challenges were about the defect in versions 1 to 4, an int
tested against a string. The escalation door then refused a second
escalation on m334. So the fixed list on `tst_2` never reached a Tester
with the running version in front of it (observed: b2q8, b2q10, b2q12).

The Tester wrote the list itself in answer mode, with the criterion's
words "the running Python interpreter version ... from sys.version_info"
in its prompt, and with the product source that formats
`sys.version_info` in its prompt. No brief and no door gave it a version
literal. Interview this authorship once (see section 5).

## 1. The test's six versions

`tests.version` reads `tst_2_flag_triggers_version_string` 6 and
`tst_1_version_output_includes_python` 2 (observed: b2q1). Each landed
encode is an `OK tests.encode -> {"id": ...}` line in the next turn's
user text. An `unchanged: True` line is not a version (observed: b2q5).

| `tst_2` version | Session, turn | Wake | Assertion line | Door result |
|---|---|---|---|---|
| 1 | s467 t3 | `tick:tests_missing` | `assert "Python" in result.output or sys.version_info.major in result.output` | OK. At t2 the file door refused: `tests/test_basic.py is already inh_dcc9ea38's file` |
| 2 | s469 t2 | message m331, challenge | the same line | OK, after a cut reply and a "no call" refusal |
| 3 | s471 t2 | message m332, challenge | the same line, plus `import click` | OK |
| 4 | s473 t1 | message m333, challenge | `assert "Python" in result.output or str(sys.version_info.major) in result.output` | OK |
| 5 | s481 t2 | message m338, answer | `assert "Python" in cmd.__click_params__[0].name  # Placeholder for actual check` | OK. At t1 the NameError door refused (`CliRunner`) |
| 6 | s488 t12 | message m344, answer | `assert "3.12" in result.output or "3.11" in result.output or "3.10" in result.output` | OK |

| `tst_1` version | Session, turn | Wake | Assertion line | Door result |
|---|---|---|---|---|
| none | s467 t2 to t5, s478 t2 to t4 | `tick:tests_missing` | `sys.version_info.major in result.output` | refused every time: plain-function door, once the surface-import door |
| none | s481 t7 | message m338, answer | the fixed list, first written | refused: the surface-import door |
| 1 | s488 t9 | message m344, answer | the fixed list (t1 wrote `"3.10"`, `"3.9"`, `"3.8"`) | OK, after five refusals at t4 to t8 |
| 2 | s492 t1 | message m348, challenge | `expected_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"` then `assert expected_version in result.output` | OK |

- The fixed list entered at s481 t7 on `tst_1` (refused), landed on `tst_1`
  version 1 at s488 t9, and landed on `tst_2` version 6 at s488 t12
  (observed: b2q5).
- Versions 1 to 4 of `tst_2` read `sys.version_info`, but the major part
  only. Versions 1 to 3 compared an int with a string, which is the
  attempt 4 `TypeError`. Version 4 used `str(...)` and failed on empty
  output (observed: b2q5, night 142 read table).
- `tst_1` version 2 is the only version that reads the full
  `major.minor.micro` from `sys.version_info`. No `tst_2` version did
  (observed: b2q5).
- The answer mode replaced a `sys.version_info` reading with a fixed list.
  The criterion did not change between the two (reasoned: the criterion
  text in s481 and s488 is the same row).
- The first sign of the literal is s473's own prose at the m333 wake:
  "checking for the *string representation* of the version (e.g., "3.10"
  or "3.11")". That prose did not reach s481 or s488. No `3.10`, `3.11`
  or `3.12` stands in any user text of s481 before t7 (observed: b2q8,
  b2q9).

## 2. The challenges

All four came from the Developer and carry `body_text` (observed: b2q6).

- m331 (s468), m332 (s470), m333 (s472), refs `c2_flag_triggers_version_string`,
  `tst_2_flag_triggers_version_string`, the same words each time: "When
  the developer passes show_python=True to the version_option decorator,
  the --version output must include the running Python interpreter
  version formatted as major.minor.micro from sys.version_info. ...
  assert "Python" in result.output or sys.version_info.major in
  result.output".
- m348 (s491), refs `c1_version_output_includes_python`,
  `tst_1_version_output_includes_python`: "'the --version output must
  include the running Python interpreter version formatted as
  major.minor.micro from sys.version_info' ... assert "3.12" in
  result.output or "3.11" in result.output or "3.10" in result.output".

Who answered: no message has `cause_id` m331, m332, m333 or m348. The
status `answered` comes from the Tester's encode (observed: b2q6). The
escalation m334 (s474, no body text) got m335 from the Architect, refs
`d1_test_encodes_criterion` and no words (observed: b2q6).

| Challenge | Tester wake | What it encoded | `3.14.2` in the prompt |
|---|---|---|---|
| m331 | s469 | `tst_2` version 2, the same assertion | no |
| m332 | s471 | `tst_2` version 3, the same assertion | no |
| m333 | s473 | `tst_2` version 4, `str(sys.version_info.major)` | no |
| m348 | s492 | `tst_1` version 2, `sys.version_info` full | yes |

The line in s492 is the pytest output in the challenge's last run:
`E       AssertionError: assert ('3.12' in 'cli, version 3.14.2 (3.14.2)\n' or '3.11' in 'cli, version 3.14.2 (3.14.2)\n' or '3.10' in 'cli, version 3.14.2 (3.14.2)\n')`.
s492's prose: "The actual output was `cli, version 3.14.2 (3.14.2)`, which
contains `3.14` but not `3.12`, `3.11`, or `3.10`" (observed: b2q8, b2q9).

The s492 prompt names `tst_2` only in the batch's test lists. It does not
show `tst_2`'s run (observed: b2q9, b2q12). m348 was about `tst_1`, so
s492 encoded `tst_1` only (reasoned: the challenge names one test).

No Tester wake that wrote the fixed list (s481, s488) had `3.14` in its
prompt. No wake of s467 to s485 had it either (observed: b2q8).

## 3. The doors

The Tester's refusals on `tst_1` and `tst_2`, with the door's sentence and
its site at 6a80be2c (observed: b2q5, `git grep`):

- Plain-function door, 16 times: "`cli` is a plain function, and calling
  it never runs the option that `version_option` adds".
  `rota/roles/api.py:6982` and `:6992`.
- Surface-import door, 4 times: "the surface
  'src/click/decorators.py::version_option' lives in decorators.py and
  this test imports from click.testing. Import the surface from its own
  module: `from click.decorators import version_option`".
  `rota/roles/api.py:6816` and `:6682`.
- NameError door: "the test uses CliRunner and never imports or defines
  it ... add `from click.decorators import version_option` and assert on
  what it returns." `rota/roles/api.py:6426`. Also "the test uses click
  and never imports it", `rota/roles/api.py:6399`.
- File door: "... is already tst_2_flag_triggers_version_string's file;
  two tests in one file overwrite each other on disk".
  `rota/roles/api.py:7240`. Also the same-criterion variant,
  `rota/roles/api.py:7228`.
- Triage repeat: "asked three times this session ...",
  `rota/core/runner.py:4057`. The "no call" lines,
  `rota/core/runner.py:2407` to `:2425`.

No Tester door names a version, a literal or the running interpreter. No
door steered the Tester toward a literal version string (observed: the
sentences above).

The doors that kept the list alive met the Developer, not the Tester
(observed: b2q10, b2q12):

- s491 t6 and s493 t1: "you sent challenge to tester on exactly these
  refs 3 times already (m331, m332, m333), and the test changed and is
  still red. End the session with no call." This is
  `_challenge_cap_refusal`, `rota/core/sandbox.py:1720` to `:1790`, with
  `LANDED_CHALLENGES = 3` at `:1583`. The cap counts every challenge on the
  refs, and does not ask whether the test version is the one challenged.
- s491 t7: "you have already sent challenge to tester; saying it again
  with different refs is a second answer to one question ...",
  `rota/core/sandbox.py:3113`.
- s491 t11: "you sent escalate to architect on exactly these refs already
  (m334) and they answered (m335): the answer points at
  d1_test_encodes_criterion. End the session with no call.",
  `rota/core/sandbox.py:2035` to `:2042`.

## 4. The brief

The Tester did not cite or restate a brief sentence when it wrote the
list. s481 t7 has no prose before the call. s488 t1 cites the
Terminologist's answer: "the output must include the running Python
interpreter version formatted as `major.minor.micro` from
`sys.version_info`", and then writes `"3.10"`, `"3.9"`, `"3.8"`
(observed: b2q8, b2q11).

The brief in the prompt at both wakes was answer mode,
`rota/roles/prompts/tester/answer.md`. Its sentence "Encode the test
against the criterion id the answer names, and call the function its
surface names after you read it with `code.source`" was in the prompt.
The seat read `code.source` of `src/click/decorators.py` at s481 t6 and
s488 t2 to t4, which shows `sys.version_info` formatted, and wrote the
literal on the next call (observed: b2q8, b2q11).

Frame 200's sentences on a test that never runs the behaviour:

- `tests_missing.md:40`, "The test calls the program: import the
  function the criterion's surface names and assert on what it returns."
  Not in the prompt of s481, s488 or s492. Those wakes are answer and
  challenge modes (observed: b2q11).
- `tests_missing.md` also has "A string the material does not fix -- a
  sample name, a prompt's wording -- is an assumption, and the encode
  records it by itself." Not in the prompt of the answer wakes (observed:
  b2q11). s488's `ledger.log` rows say "The test asserts that show_python=True
  triggers inclusion of the Python version in the message." They name no
  version (observed: b2q11).
- `answer.md`'s surface sentence was in the prompt. The seat obeyed it:
  every answer-mode encode calls `version_option` through `CliRunner`.
  The seat wrote nothing about these sentences (observed: b2q8, b2q11).
- No Tester brief holds a version literal, "hard-code", "running" or
  `sys.version` (observed: `git grep` on `rota/roles/prompts/tester/`).

## 5. One line

**Survival is a door case: no prompt that could change `tst_2` version 6
carried `3.14.2`, because the challenge cap counted m331 to m333 on an
older defect and refused the Developer's challenge on version 6 (s491 t6,
s493 t1). Authorship is an interview case: s481 t7 wrote a fixed list
with "the running Python interpreter version ... from sys.version_info"
and the source's `sys.version_info` format in its prompt. Replay
`--seq` for session s481, turn 7** (reasoned: sections 2 to 4). The one
wake that had `3.14.2`, s492, acted on it (observed: b2q5).
