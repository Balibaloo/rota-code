# Frame 326's residue, the provenance read: the copy guard of `code.write`

Date: 2026-10-26. Read at commit d03d1bca on `rota/foundation`. Read-only. No
model ran and no test ran. One script read `FILES` of
`rota/testkit/samplerepo.py` in the session scratchpad. Meta workflow for the
read, by the rule of 2026-10-18 (provenance before a fix). The symptom record
is `plans/gate150607c1-reds.md` section 1, and this record does not repeat it.

Sources:

- `rota/roles/api.py` at d03d1bca: the Python block of `code_write` from 18714,
  the copy guard 18884 to 18938 (`had_before` 18894 to 18906, the index query
  18912 to 18919, the worktree read 18923, `named_here` 18930, the refusal 18931
  to 18938), the fence baseline 18943 to 18958, `_base_text` 20546,
  `_defined_in_tree` 22585 to 22604.
- `git log -L18884,18945:rota/roles/api.py`. `git log -S` on "name the project
  has once is a copy", `had_before`, `def _defined_in_tree`,
  `root.rglob("*.py")`, `named_here`, and the query string
  `SELECT grain FROM code_index WHERE grain_kind = 'symbol'`.
- Commits 795821f9, f177cae7, 769bbf96, 57705380, 09891c33, 21f0e7b0, with
  their messages and their test hunks.
- `plans/wake-audit.md` rows 7, 8, 27 and 33 (lines 36, 37, 56, 62).
- `plans/night138-read.md` lines 115 to 128 (section 3). `plans/stack.md`
  frame 194 (lines 2373 to 2381) and the frame 114 status line 2909.
- `rota/DECISIONS.md` lines 1486 to 1511, "A write is permitted on any file,
  and an unexpected change goes to the Architect (2026-10-17)".
- `rota/LAWS.md` law 12, lines 325 to 343. `plans/wall-guide.md` lines 560 to
  573.
- `rota/onboarding/indexer.py` lines 53 to 59 and 120 to 130 (tree-sitter,
  one parser per language).
- A search of `rota/DECISIONS.md`, `rota/LAWS.md`, `rota/design/`,
  `plans/composition.md` and `plans/wall-guide.md` for a copy rule, a "second
  definition" rule and a duplicate-name door.

## The result

**Verdict: a gap, not a departure.** The build session made the copy guard
on 2026-09-13 from a wake-audit finding, and no ruling of Roman names it
(observed: commit 795821f9; the search above found no copy rule in
`DECISIONS.md`, `LAWS.md` or `rota/design/`). The guard has two gaps, and
neither was a choice with a reason. `had_before` read the working file on the
same day that the fence got the same working-file baseline, and frame 220
moved only the fence to the batch's base commit on 2026-10-17 (observed:
57705380, f177cae7, 21f0e7b0). The index query never had a language filter.
The guard was born on a multi-language index, and its worktree read was born
Python-only three hours later (observed: 795821f9, 769bbf96, indexer.py 53 to
59). The ruling of 2026-10-17 on writes does not decide either gap, so no
question for Roman stands (reasoned: section 6).

## 1. Which ruling or design made the copy guard

1. **No ruling of Roman made the guard.** The search found no copy rule, no
   "second definition" rule and no duplicate-name door in `DECISIONS.md`,
   `LAWS.md`, `rota/design/graph.json`, `stories.json` or `composition.md`
   (observed: the search). `plans/wall-guide.md` names "the copy door" as a
   site of the two-writers cause, not as a rule (observed: wall-guide 566).
2. **The build session made the guard.** Commit 795821f9, 2026-09-13 14:46
   +0100, "a copied unique name is refused" (observed: `git log -S` on the
   refusal text). Its message cites the wake audit of night 35: the Developer
   wrote its own `def echo` in `src/click/main.py`, and nights 32 to 34 wrote
   `echo_json` a second time (observed: the commit message). The workflow was
   the wake audit of `plans/wake-audit.md`, row 8, before the stack held
   numbered frames for doors (observed: wake-audit line 37).
3. **Three commits changed the guard since** (observed: `git log -L` on 18884
   to 18945):
   - 769bbf96, 2026-09-13 17:36: the guard also reads the batch's worktree,
     `_defined_in_tree`, from wake audit row 27 on night 42.
   - 57705380, 2026-09-13 22:44: `had_before`, a file may keep a name it
     defined before, from wake audit row 33 on tipsBF.
   - 09891c33, 2026-09-14 01:52: `named_here`, the guard yields for a file a
     criterion names, from the case `L1-DV-build-a-clear-criterion`.
   - f177cae7 (2026-09-13) and 21f0e7b0 (2026-10-17) appear in the range only
     through the fence below the guard. They did not change the guard.

## 2. Which build decision shaped `had_before` to read the working tree

1. **The two baselines started on the same day with the same read.** The
   fence took "the original file as a baseline" in f177cae7, 2026-09-13 15:52,
   and the code read `target.read_text` (observed: the commit message, and
   the fence's first `_baseline.append` at api.py 18949). `had_before` took
   the same `target.read_text` in 57705380, 2026-09-13 22:44 (observed: api.py
   18900 to 18903). Both were wake-audit fixes of the build session on
   2026-09-13 (observed: wake-audit rows 15, 16 and 33). The commits carry no
   session id, so this read cannot prove one session wrote both.
2. **The fence moved to the base commit, and the guard did not.** Commit
   21f0e7b0, 2026-10-17 23:04, frame 220, law 12, added `_base_text` to the
   fence's baseline after night 154's b4. There, 16 restores were refused
   because a reach the batch's own write removed read as a new reach on the
   way back (observed: the commit message; stack line 2909). The fence
   starts 5 lines below the guard's end in the same function, and the commit
   left the guard unchanged (observed: `git show 21f0e7b0`).
3. **The working-tree read was a default nobody named.** The tipsBF case of
   57705380 is a whole-file rewrite of a file the batch had not changed, so
   the working file and the base file were the same (observed: the test
   `test_a_file_may_keep_a_name_it_already_defined`,
   `tests/rota/test_touch_divergence.py:219`, writes the files with no git
   history). No record names the choice between the two baselines (observed:
   the search; the commit message says only "the tree's own duplicate is not
   this change's"). The DECISIONS entry of 2026-10-17 names frames 220 and
   286 as the fixes, and it does not name the copy guard (observed: DECISIONS
   1509 to 1511).

## 3. The language and grain filter on the index query

1. **The index query never had a language filter.** The query of 795821f9
   reads `grain_kind = 'symbol' AND grain LIKE '%::name'` with no suffix
   test, and the text at d03d1bca is the same (observed: `git show 795821f9`,
   api.py 18912 to 18919; `git log -L` shows no later change to these lines).
   The grain filter is `symbol` from the start, so a `path` row never matched.
   A method grain `Class.method` does not end in `::name`, so the query
   matches top-level grains only (reasoned: the `endswith` test at 18916).
2. **The index was multi-language before the guard existed.** The indexer
   parses each file with a tree-sitter parser for its language, from 7da68101,
   2026-08-10 (observed: indexer.py 53 to 59 and 120 to 130; `git log` on the
   indexer). `web/format.js::truncate` is in the sample repository from
   58642fc1, 2026-08-10 (observed: `plans/gate150607c1-reds.md` section 1).
3. **`_defined_in_tree` was limited to `*.py` at its birth.** Commit 769bbf96,
   2026-09-13 17:36, wrote `root.rglob("*.py")` and a regex for `def`,
   `async def` and `class` (observed: `git log -S 'def _defined_in_tree'`,
   api.py 22593 and 22596).
4. **Why the two checks disagree.** The regex reads Python syntax, so the
   `*.py` limit follows from the regex (reasoned). The index query reads rows
   that the indexer writes for every language, and 795821f9 adds no suffix
   test and no comment on languages (observed: the commit). The guard runs
   only inside `if path.endswith(".py")` at api.py 18714, so the written file
   is always Python (observed: 18714). So only a Python definition elsewhere
   can be the first one that "the tests and the callers reach" (reasoned: the
   refusal text at 18936 to 18937; a Python caller cannot reach a JavaScript
   export).
5. **The gap was hidden until frame 326.** The case fixtures had an empty
   index, so only `_defined_in_tree` answered, and it reads `*.py` (observed:
   `plans/gate150607c1-reds.md` section 1). A night onboards and fills the
   index, so a night meets the cross-language match (reasoned).

## 4. Whether the build met the design's own condition

1. **The guard's first build measured nothing on a night at its close.** Wake
   audit row 8 records the door and no measurement (observed: wake-audit line
   37). Nights 35 and 36 "ran from a scratchpad copy of the gauntlet script",
   and "the nights' outcomes are not measurements" (observed: wake-audit row
   7, line 36).
2. **Each change was closed on one case.** 795821f9, 769bbf96 and 57705380
   each added tests to `test_touch_divergence.py`. 09891c33 closed on the
   re-record of 2026-09-14: "28 stale cases, 20 green, 8 red and attributed"
   (observed: the commits' stats and messages). No record counts right
   refusals against wrong ones at any close (observed: the search of
   `wake-audit.md` and `stack.md`).
3. **The first count came from a different frame.** Night 138's read counts
   the copy door in 13 Developer sessions on b_1, 1 to 7 refusals each. Each
   fire was right by the guard's rule, because `echo_json` stood in
   `src/click/utils.py` (observed: `plans/night138-read.md` lines 115 to 128).
   That count serves frame 194, the copy door against the surface door, which
   is still open (observed: wall-guide 572 to 573).
4. **A whole-file write-back after a partial drop was never a case.** The
   test of 57705380 writes each file once, with no earlier write in the
   session (observed: the test hunk). The shape first appeared as a refusal
   on the gate at 150607c1 (observed: `plans/gate150607c1-reds.md` section 1).
   The fence met the same shape on night 154, and frame 220 fixed the fence
   (observed: stack line 2909).

## 5. What else the guard refuses today on the sample repository

The script read the 34 files of `FILES`: 24 `.py`, 4 `.js`, 1 `.sql`, 3 `.md`,
1 `.toml` and 1 `.gitignore` (observed: the script). It counted the top-level
`def`, `class`, `function`, `const` and `let` names of the non-test files.

1. **Two names are defined in more than one file, and both pairs cross
   languages** (observed: the script):
   - `money`: `src/notify/templates.py` and `web/format.js`.
   - `truncate`: `src/notify/formatting.py` and `web/format.js`.
2. **No public Python name is defined in two Python files** (observed: the
   script). 42 public Python names are defined once in the project, and a
   whole-file write-back of each passes (reasoned: `elsewhere` is empty).
3. **Two Python names are refused on a whole-file write-back after a partial
   drop**: `truncate` in `src/notify/formatting.py` and `money` in
   `src/notify/templates.py`. Both match only `web/format.js` (reasoned: the
   guard's rule applied to the script's counts). `money` is the same wall in
   a second file, and no case holds it yet (reasoned).
4. A side fact: `src/auth/accounts.py` does not parse. Its body is a raw
   string at `samplerepo.py:230`, so the docstring at line 242 keeps its
   backslashes (observed: `ast.parse` raised `SyntaxError`). On that file
   `had_before` is empty, so the guard treats every name of the file as new
   (observed: api.py 18905 to 18906). None of its names is defined twice, so
   the guard refuses nothing there today (observed: the script).

## 6. Whether a design departure stands

No ruling of Roman covers the guard's baseline or its languages. The nearest
ruling is of 2026-10-17 at about 16:50: "File writes were always permitted
everywhere, just that if there were unexpected changes then the architect is
required to sign off" (ruled: Roman, `rota/DECISIONS.md` 1488 to 1493). Its
recorded consequence covers a door that refuses "because no criterion names
it", and it keeps a door that gates on a fact of the text (observed: DECISIONS
1500 to 1508). The copy guard gates on a fact, the second definition, and its
own commit says "the door holds file facts only" (observed: 09891c33). So the
ruling does not decide the guard (reasoned). The repair below keeps the guard
a fact door and makes the fact true. A restore of the base commit's own name
is not a change, so the repair agrees with the ruling (reasoned).

## The repair

Add to `had_before` the top-level names that the file defines at the batch's
base commit, read with `_base_text` as the fence reads it below the guard.
Keep only index rows whose path ends in `.py`, as `_defined_in_tree` already
does. The red test: in a git worktree whose index holds
`web/format.js::truncate`, a partial write drops `truncate` from
`src/notify/formatting.py`, a whole-file write puts the base text back, and
the write passes. A new `truncate` in a new Python module beside a Python
`truncate` is still refused.
