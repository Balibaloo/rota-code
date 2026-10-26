# Frame 328, pass 4, the provenance read: the test path and the collection error at `tests.encode`

Date: 2026-10-26, read at 07:36 to 07:41. Read at commit 6cb851c8 on
`rota/foundation`, dated 2026-10-26 07:32. `rota/` is the same at 4bb2656b
and at 6cb851c8 (observed: `git diff 4bb2656b HEAD --stat -- rota/`, empty).
Read-only. The five night databases were opened with `?mode=ro`. No model
call ran and no pytest ran. Meta workflow for the read, by the rule of
2026-10-18 (provenance before a fix).

Sources:

- The symptom records, cited and not repeated: `plans/night167-cycle1.md`
  (the result, section 1); `plans/night167-read.md` section 2 rows W2 and
  W7 (lines 95 and 100), section 3 row 328 (line 115), section 5 row 2 and
  C1 (lines 280 and 293 to 302).
- `plans/stack.md` lines 1143 to 1171 (frame 328), lines 25 to 60 (sprint 24).
- `rota/roles/api.py`: `tests_encode` 9182 to 9290 (the path check 9264 to
  9267, the backslash form 9203 to 9206, `fence.check` 9277), the run door's
  call 10773 to 10778, `_refuse_unindexed_files` 7404 to 7500 (`test_shaped`
  and `test_dirs` 7439 to 7443), `_encode_run` 17261 to 17283,
  `_developer_committed` 17320 to 17327, `_own_assertions` 17330 to 17370, `_arrange_run_refusal` 17373 to 17460
  (the silent return 17411 to 17412), `_unloadable_surface` 17744 to 17758.
- `rota/core/harness.py` 204 to 264 (`_run_one`), line 28 (`EXIT_OK`,
  `EXIT_FAILED`). `rota/core/lifecycle.py` 405 to 428 (the journal write).
  `rota/core/schema.sql` 590 to 599 (`test_run_journal`).
- `rota/core/runner.py` 4692 to 4701 (the `touch` key of the Tester's wake).
- `rota/roles/prompts/tester/tests_missing.md` lines 5 to 7 and 35 to 40,
  `answer.md`, `challenge.md`.
- `rota/DECISIONS.md` 943 to 968, "Harness facts are refused at the door".
- `plans/frame304-review-2.md` line 16. `tests/rota/test_frame304_arrange_door.py`
  98 to 121. `tests/rota/test_frame328_*.py`.
- `rota/testkit/samplerepo.py` lines 676 to 713 and 812.
- `.rota/clickI_night163.db` to `.rota/clickI_night167.db`: `tool_calls`
  (`fn = 'tests.encode'`), `turns`, `sessions`, `tests`, `code_index`,
  `batch_touch`, `test_run_journal`.
- `git log -S` on "is not a Python file", "name the file test_<thing>.py",
  `if not path.endswith(".py"):`, `if verdict != "fail":`, "One form of the
  path for every door", "collection error where the door is silent";
  `git log -L` on `api.py` 9264 to 9267 and on the silent return.

## The result

**Verdict: a gap, not a departure. No ruling and no design names where a
test file lives, and the silence on a collection error is a default that a
later pass turned into a reason for one case only.** The path check was
built on 2026-09-01 to refuse a path that is not Python, and it never read
the folder (observed: bfd149d1). The encode run reads only the word `fail`.
A collection error is the word `error`, so the run door returns `None` and
writes no note (observed: `api.py` 17411 to 17412; `harness.py` 260 to 264).
Frame 304's review 2 named that silence on 2026-10-23, and pass 2c used it as
the reason to keep a failed import silent before the code exists (observed:
`plans/frame304-review-2.md` line 16; 8a5b3390). Nobody named the case after
the Developer's commit, which is the case of night 167 (reasoned: the
`_developer_committed` gate of 8f960862 applies only to `fail`).

Two causes sit behind the path itself. The `answer` and `challenge` briefs
name no path form, and all 31 encodes at a `src/` path on nights 166 and 167
came in those two modes (observed: `sessions.wake_kind` and the `MODE:` line
of the first turn). The `tests_missing` brief says "A path under `touch` is
the file the principal expects your tests in", and the Tester's wake on night
167 showed `"expected to touch": ["src/click/utils.py"]` (observed: s324 to
s343, the first turn's user text). Cause 9 by `plans/wall-guide.md`: the word
`touch` names two lists (reasoned).

## 1. Which ruling or design made the path check

The check is `api.py` 9264 to 9267: `if not path.endswith(".py")`, with the
refusal "path ... is not a Python file. The harness runs pytest; name the
file test_<thing>.py" (observed). Commit bfd149d1, 2026-09-01 20:14, "fix(sandbox):
a test is Python the harness can run", added it (observed: `git log -S` on
both refusal strings and on the condition, one commit each). It served S0,
the first walk series, and the build workflow of that time. Its reason:
"the Tester claims encodable and encodes the criterion as an English
sentence at path 'script'" (observed: the commit body). The check refuses a
path that is not Python. It was never meant to read the folder (reasoned:
the commit body names only the extension).

`git log -L` on the four lines shows bfd149d1 alone. The check is unchanged
since (observed). One later commit changed the path before the check:
a71951a7, 2026-10-05, writes every backslash as `/`, because a stored
backslash path ran as "no tests ran" (observed: `api.py` 9203 to 9206).

The rule search found no rule on where a test file lives:

- `rota/DECISIONS.md`, `rota/LAWS.md`, `plans/wall-guide.md`: no rule on a
  test folder or a test path (observed: grep on "test folder", "test path",
  "tests/", "test file", "test directory"). DECISIONS line 163 names
  `tests/*` as proposed survey areas only.
- `rota/design/`: no match in `stories.json` or `graph.json` (observed).
- `plans/stack.md`: no earlier frame on a test path. Line 2566 counts test
  paths in survey bindings, a different subject (observed).
- The nearest code: `_refuse_unindexed_files` defines `test_shaped` and
  `test_dirs`, frame 302, 2b5b39cd, 2026-10-23. It serves the Architect's
  annotate door and not `tests.encode` (observed: `api.py` 7439 to 7443).
- The nearest design: "Harness facts are refused at the door",
  DECISIONS 943 to 968, built 2026-09-02, e4820c34. It lists "two tests on
  one path overwrite each other on disk" and "a module the tests import that
  reads stdin at import dies at collection" (observed). A test file that
  replaces the module it imports is the same class of fact: certain on any
  code (reasoned). The list never took it.

## 2. Which build decision made a collection error silent at encode

The run at encode is `_encode_run`, `api.py` 17261 to 17283. It writes the
body at its path in the batch's worktree, calls `harness._run_one`, and puts
the old bytes back (observed). The reader is `_arrange_run_refusal`, 17373 to
17460. Line 17411 is `if verdict != "fail": return None` (observed). The
encode note of pass 1 (17430 to 17457) and `encode_noted` (17447) sit after
that line, so they read `fail` only (observed).

`_run_one` maps the pytest exit code to one word, `harness.py` 260 to 264:
exit 0 is `pass`, exit 1 is `fail`, every other exit is `error` (observed).
A collection error is exit 2, "Interrupted: 1 error during collection". A
body with 0 collected tests is exit 5. Both are `error` (observed:
`test_run_journal` seq 318 of night 167, `result = 'error'`, that summary
line; reasoned for exit 5 from the same branch). The docstring states the
split as a design: "`fail` says the code is wrong, `error` says the test
could not answer" (observed: `harness.py` 216 to 219, b519a246 2026-08-10).
So the word is a choice with a reason. The silence at encode is not.

The encode run writes no journal row. `_encode_run` returns `(verdict,
said)` and stores nothing (observed: 17261 to 17283). `test_run_journal` is
written only by `lifecycle` 405 to 428, from the harness's batch run, with
the fields `test_id`, `commit_sha`, `result`, `output` and `attempt`
(observed). The encode read uses the word and the output tail only.

The history of the silent line:

1. a3ce3f01, 2026-10-23 18:27, frame 304, added `_arrange_run_refusal` with
   line 17411. The commit body names stubs and arrange raises, not
   collection (observed: `git log -L` and the body). A default nobody named
   (reasoned).
2. `plans/frame304-review-2.md` line 16, 2026-10-23 18:17, named it: "A
   module-level import gives a collection error, the word is `error`, and the
   door is silent" (observed).
3. 8a5b3390, 2026-10-23 18:56, pass 2c, used that silence as the reason to
   admit an import line in the body: "The Developer or an install adds the
   module, and the same import at module level is a collection error where
   the door is silent" (observed: `test_frame304_arrange_door.py` 104 to
   108). The reason holds before the code exists (reasoned).
4. Frame 328's pass 2b, 8f960862 on the branch as 73c57a08, gates the note on
   `_developer_committed`, so the note fires only after the code exists
   (observed: stack line 1161; `api.py` 17442 to 17444). The gate covers
   `fail` and not `error` (observed: 17411). Night 167's bg_6 had the
   Developer's commit fa4e8230 when s326 encoded (observed:
   `night167-cycle1.md`, the result).

## 3. What the Tester's briefs and the refusal texts say about the path

- `tests_missing.md` lines 5 to 7: "A path under `touch` is the file the
  principal expects your tests in. Use it." Added by 2dace61b, 2026-10-09,
  frame 190 (observed).
- `tests_missing.md` lines 35 to 38: "the path is `tests/test_<thing>.py`",
  and the example `tests.encode(id='tst_1', criterion_id='c1',
  path='tests/test_prorate.py', ...)` (observed).
- `answer.md` and `challenge.md`: no path line and no `tests.encode` example
  with a path (observed: grep on "path" and "tests/"). Every encode at a
  `src/` path on nights 166 and 167 ran in these modes: night 166 s117, s119
  and s121, `answer`; night 167 s326, s333 and s343 `answer`, s329 and s335
  `challenge` (observed: `sessions`, the first turn's `MODE:` line).
- The `touch` key of the wake holds only paths that start with `tests/`
  (observed: `runner.py` 4692 to 4701). bg_6 had no such path, so the key was
  absent. The batch view still showed `"expected to touch":
  ["src/click/utils.py"]` (observed: `batch_touch` of bg_6; s326 turn 1 user
  text). The brief's word `touch` reads as that list (reasoned).
- The extension refusal names a basename form, `test_<thing>.py`, and no
  folder (observed: `api.py` 9266 to 9267).

s329's refusal named the surface and not the path, by the row. s329 turn 7's
user text holds "ERROR tests.encode: the criterion's surface
'src/click/utils.py::format_filename' lives in click.utils, and click.utils
does not load in the sandbox the tests run in: ImportError: cannot import
name 'format_filename' from partially initialized module 'click.utils' ...
Do not import click.utils" (observed: `turns` s329 seq 7). The text comes from
`_unloadable_surface`, `api.py` 17744 to 17758 (observed). The door probed
the module while the stored test sat at the module's path, so it blamed the
criterion's surface and told the Tester not to import it (reasoned).

## 4. Whether passes 1 to 3 met the first clause's condition

The clause: a test written on a batch with a head runs at encode, and a red
goes back to the Tester with its failing line (observed: stack line 1146).

| Pass | Status line | What it measured on the encode run |
|---|---|---|
| 1, 0b98954c | stack 1158 | A red at an assertion in the test's own file gives the note. s198's test, red on `KeyError: 'note'` |
| 2, 9913fc88 and 5d76fddc | stack 1159 | The quote check and the green-test challenge. The encode run is not a subject |
| 2b, 8f960862 | stack 1161 | The note only after a Developer's `code.commit`, with each red test's own line |
| 3, d72efa4c | stack 1168 | The one-test guard reads staged encodes, so the re-encode after the note lands |
| 3b, ed143a31 | stack 1170 | Control-character escapes in the quote check |

Each pass measured a red at an assertion, `fail`. No pass measured `error`
(observed: the five status lines). The frame 328 test files hold no
collection-error case: `test_frame328_encode_note.py` spies `_encode_run` and
reads `fail`, and `test_frame328_restage.py` writes a `'fail'` run (observed:
grep on "error" and "collect"). The one collection case in `tests/rota/` is
`test_frame304_arrange_door.py` 98 to 121, and it pins the silence (observed).
So the clause was met for `fail` and not for `error`. Night 167 shows the
missing half: 3 collection errors with no note, tst_c4, `'tst_c5` v1 and
tst_c1 v1 to v4 (observed: `night167-read.md` line 115).

## 5. What a path door would refuse today that is right

Encodes by folder, from `tool_calls` with `fn = 'tests.encode'`, all Tester
seats (observed):

| Night | Model | Calls | Under `tests/` | A program file under `src/` | `src/...::symbol` | Beside the module | Other |
|---|---|---|---|---|---|---|---|
| 163 | qwen3.5:9b | 30 | 30 | 0 | 0 | 0 | 0 |
| 164 | qwen3.5:9b | 95 | 79, and 16 with the path cut from the summary | 0 | 0 | 0 | 0 |
| 165 | qwen3.5:9b | 446 | 151, and 295 with the path cut | 0 | 0 | 0 | 0 |
| 166 | qwen3.5:9b | 51 | 33 | 14, `src/click/utils.py` | 2 | 0 | 2, `test_utils.py` at the root |
| 167 | gemma4:12b-it-qat | 62 | 47 | 15, `src/click/utils.py` | 0 | 0 | 0 |

The cut paths on nights 164 and 165 are `tests/` paths: every `tests.encode`
call in those nights' Tester completions names `tests/` (observed: a parse of
`turns.completion`; reasoned that the cut rows are the same calls). The
`src/` count is 0, 0, 0, 16 and 15, as the night read says.

Stored tests by folder: 36, 40, 42, 45 and 41 under `tests/` on nights 163 to
167, and 1 at `src/click/utils.py`, night 167's tst_c1 at version 4 (observed:
`tests`). No stored test sits beside its module, so no such test ran green or
merged (observed). The sample repository holds 3 test files, all under
`tests/`, and its stage list reads `p.startswith("tests/")` (observed:
`samplerepo.py` 676 to 713 and 812).

A door that refuses a path that is a program file of the code index refuses
0 right tests on these records (reasoned: every refused call above is a wrong
path). A door that refuses any path outside a test folder also refuses the 2
root `test_utils.py` calls of night 166, which were not stored (observed).

## 6. Whether a design departure stands

No ruling of Roman's covers where a test file lives or what an encode run
reports (observed: the search of question 1). The two nearest records are
not his: frame 190's question 5.2, "ruled on the records by the holding
session, 2026-10-09" (observed: `runner.py` 4692 to 4695), and the build's
design "Harness facts are refused at the door", 2026-09-02. The build did not
depart from either. It left the case out (reasoned).

## The repair

1. The path door. In `tests_encode`, after the extension check, refuse a
   path that is a program file of the code index outside the test folders,
   and name the test folders the index holds with a `test_<thing>.py` path in
   one of them. Lift `test_shaped` and `test_dirs` out of
   `_refuse_unindexed_files` so both doors read one rule. Red tests: s326 t3,
   `path='src/click/utils.py'`, and night 166's s117, the same path.
2. The collection error as a red. In `_arrange_run_refusal`, after the
   Developer's commit, read an `error` run whose output holds "error during
   collection" as a red and give the Tester the note with the `E` line and the
   collecting file. Before the commit, keep pass 2c's silence for an import of
   a project name. Red tests: s326 t3 run at fa4e8230, and s142 t2's tst_c4.

The brief residue is one line in `answer.md` and `challenge.md` that names
the test path form, and a rename of the wake's `touch` key or of the brief's
word. It is a candidate for the same pass, and it is priced after the doors
(reasoned: the doors are mechanical, and the brief fix is measured on a
night).

## Usage

One agent on Opus. About 80k tokens of context against the 60k cap. Not read:
whether s142 t2's batch had a Developer commit when tst_c4 was encoded, which
the second red test needs; the exit code of a body with 0 tests, read from the
code and not from a run.
