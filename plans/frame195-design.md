# Frame 195 design: the red row carries the exception a `CliRunner` caught

Status: drafted 2026-10-11 by session 84ce0759 from the scope report
`plans/frame195-scope.md`. Design review on Opus, 2026-10-11 03:03, `plans/frame195-design-review.md`: start after the fixes in the section below. Rota workflow.

## The fault

On night 138 every b_3 commit used `sys.version` with no `import sys`. The
Tester's test called the command through click's `CliRunner`. The runner
caught the `NameError`, stored it in `result.exception`, and the test
asserted on `result.output`, which was empty. The red row the Developer
read said `AssertionError: Expected Python version string in output: `
for eight attempts, and the Developer never saw the exception (observed:
`plans/night138-read.md`, section 4).

The scope found a second fault in the same row. `tests.load` adds a
`raised at` line from the last `path.py:N: XxxError` line of the output.
That line was the test's own assertion, so the wake said `raised at:
tests/test_version_option_version_format.py:17, the test's own assertion`
and pointed the Developer at the test and not at its code, in 9 Developer
sessions of walk 3 (observed: `plans/frame195-scope.md`, section 2).

The harness gets text only. The `Result` lives in the pytest child, and
`test_runs.output` holds the last 2000 characters of that text
(`rota/core/harness.py:171`). So the fix sits inside the test process.

## The design: a plugin that reports the caught exception

The scope's option (d). The harness runs every batch test with a pytest
plugin. The plugin reports an exception a `CliRunner` caught on a test that
fails. It changes no test's result.

1. **The plugin module.** A new file in a directory that holds plugins
   alone, for example `rota/core/plugins/pytest_caught.py`. It imports
   `pytest`, `os`, `sys` and `traceback` and nothing from rota, because it
   runs under the project's interpreter.
2. **The load.** `harness._run_one` adds `-p pytest_caught` to the pytest
   command, and `execute.run` gains an `env` argument, a mapping merged
   over the process environment, through which the harness prepends the
   plugin directory to `PYTHONPATH`. No file is written into the worktree,
   so no diff or commit can carry the plugin.
3. **The wrap.** Before each test's call, the plugin imports
   `click.testing` inside a `try` that swallows `ImportError`, and wraps
   `CliRunner.invoke` once, marked so a second wrap does not stack. The
   wrapper calls the original, passes every argument and the return value
   through unchanged, and keeps each `Result.exc_info` whose exception is
   not a `SystemExit`. The import before the call closes the gap where a
   test imports `click.testing` inside its own body. A project with no
   click pays one failed import per test and nothing else.
4. **The report.** On a failed `call` report with a kept exception, the
   plugin appends a section titled `CliRunner caught an exception`. The
   section holds the last three frames of the traceback with paths
   relative to `rootpath`, the exception line, and a final line
   `<relative path>:<line>: <ExceptionName>`. pytest prints sections after
   the traceback, so that line is the last match for `raised at`. The
   section stays under about 600 characters, so the 2000-character tail
   keeps both the test's assertion and the caught exception (observed: the
   probe in `plans/frame195-scope.md`, section 3, 3240 characters with
   absolute paths and the assertion line dropped).
5. **The words.** `tests.load` at `rota/roles/api.py:7069` gains a third
   wording. When `said` holds the section title, the line names the caught
   exception, its file and line, says that the runner caught it inside the
   command so `result.output` was empty, names the assertion that then
   fired, and says whether the file is one the diff touched. The two
   wordings of today stay for the rows with no section. The phrase `before
   any assertion ran` is false for a caught exception, and must not appear
   on that row.
6. **What the plugin does not do.** It does not change
   `catch_exceptions`. It reports no `SystemExit`, because click exits that
   way on purpose. It does not run on the project's tests differently from
   the batch's own: the same plugin loads on both, and a project test that
   asserts a caught exception keeps its result.

## The review's fixes, folded in (2026-10-11)

The review reproduced four ways the plugin of items 1 to 4 changes a
test's result, and found two gaps. Each fix below replaces the item it
names.

1. The module is `_rota_caught`, a name no project file is likely to
   hold, because `python -m pytest` puts the working directory ahead of
   `PYTHONPATH` and a project file of the same name replaced the plugin
   (observed: the review's shadow probe). The harness adds
   `--show-capture=all` to the command, because a project's `addopts =
   --show-capture=no` hides every section and a command-line value wins.
   The plugin's syntax stays old: no `match`, no new f-string forms,
   because it runs under any Python a project venv has.
2. The import of `click.testing` runs only when `"click"` is in
   `sys.modules`, inside `warnings.catch_warnings()` with
   `simplefilter("ignore")`, and catches `Exception`, not `ImportError`.
   A stub that raised `NameError` at import, and one that warned under
   `filterwarnings = error`, each turned a pass into a fail (observed: the
   review's stubs).
3. The wrapper carries `functools.wraps(orig)`, because a test that reads
   `inspect.signature(CliRunner.invoke)` failed on `(self, *a, **k)`. The
   inspection of the result sits in `try/except Exception`, because a diff
   that stores `exc_info` as an exception and not a tuple raised inside
   `invoke`. The plugin formats the traceback text at once and keeps the
   text, never `exc_info`, so no frame stays alive into the next test.
   The report hook is guarded the same way: an exception in it gave
   `INTERNALERROR` and exit 3, which the harness records as `error`.
4. The section dedupes its entries by exception type, file and line, and
   keeps one entry plus `and N more`, because four raising calls pushed
   the assertion line out of the 2000-character tail and five dropped the
   title. `os.path.relpath` falls back to the absolute path when it raises
   `ValueError`, because base Python is on `C:` and the worktrees on `D:`.
   The section also records whether `result.output` was empty, as a fact
   line, for example `output: empty` or `output: 42 characters`.
5. The section's final line carries a fixed prefix:
   `caught by CliRunner at <relative path>:<line>: <ExceptionName>`. The
   third `raised at` wording reads that line with its own pattern and not
   `frames[-1]`, because the regex of today misses a custom exception
   class, a `StopIteration` and a frame in `<string>`. The wording states
   the facts: the exception, its file and line, that the runner caught it
   inside the command, whether the output was empty, the assertion that
   fired, and whether the file is one the diff touched. No `so`, because
   a command can echo text and then raise.
6. The plugin loads on the project's tests and on the batch's own tests
   alike. Night 138's project test `inh_dcc9ea38` failed beside `tst_v3`
   at 3eebc90, and a plugin on the own tests alone would leave that row
   with the false assertion pointer.
7. The measure counts Developer `tests_failing` sessions whose turn 1
   shows an empty-output red with no section, because `test_runs` keeps
   only attempts 4, 6, 7 and 8 of b_3. Baseline: 10 of 11 sessions on
   night 138's b_3, s380 to s393 (observed: the review's query on a copy
   of `.rota/clickI_night138.db`). The query:

   ```sql
   SELECT s.id, s.wake_detail,
          max(instr(t.user,'Expected Python version string in output: ')>0),
          max(instr(t.user,'CliRunner caught an exception')>0)
   FROM sessions s JOIN turns t ON t.session_id=s.id
   WHERE s.role='developer' AND s.wake_kind='tick:tests_failing'
     AND s.wake_refs LIKE '%"b_3"%' AND t.seq=1
   GROUP BY s.id ORDER BY s.seq
   ```

   Target: at most 1 in 5 on the walk, with the residue rule as before.

## Why not the other options

- A default of `catch_exceptions=False` turns 3 failed into 23 failed on
  click's own suite at 3eebc90, because the patched class is the code
  under test, and up to 11 of 57 night Tester bodies assert on the caught
  exception (observed: `plans/frame195-scope.md`, section 5a).
- A brief line re-records 13 Tester cases and depends on the seat. A door
  fails the certainty rule of `DECISIONS.md:943`, because a test may
  assert a caught exception on purpose. Neither repairs the `raised at`
  line (reasoned: section 5c of the scope).

## Tests, no model

- The plugin, through a subprocess pytest run on a temporary tree: a stub
  `click/testing.py` whose `CliRunner.invoke` catches exceptions; a
  failing test whose command raises `NameError` prints the section and
  the final line; a passing test prints no section; a `SystemExit` prints
  no section; a test that imports `click.testing` inside its body is
  reported.
- The harness: `harness.run` on a tree with the stub carries the section
  into `test_runs.output`, and the 2000-character tail holds both the
  assertion and the final line on night 138's shape, from the probe's
  output as a fixture.
- `tests.load`: the `raised at` words on tr532's text with the section,
  on tr532's text alone, and on a row with a non-assertion error and no
  section.
- `execute.run`'s `env` argument reaches the child.

## The measure on the walk

Superseded by fix 7 above: Developer `tests_failing` sessions whose turn
1 shows an empty-output red with no section, 10 of 11 on night 138's b_3,
to at most 1 in 5 on the walk, with the residue rule as frame 193 wrote
it: a session that still shows the sign is read, and the frame closes
when its cause is not the hidden exception.

## Cost

One implementer pass on Opus, about 300k cold. 0 re-records, because the
Developer's prompt changes only on a row that holds the section, and no
recorded case holds one (reasoned: section 5d of the scope). One design
review and one diff review, about 100k each. The walk is the next night,
frame 200's or an earlier one.
