# The sweep: design record and brief (frame 24, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the post-mortem of frame 21, change 1. Amended after the
design review of 11:40 (reviewer type on Opus, 23 tool calls, 66k, ten
findings, cited as R<n>). The implementer builds from the brief. The
reviewer read this record before any code.

## Why

Frame 21 swept 48 test files by hand through four sub-agents: about 30
minutes and about 0.6M tokens, none of it reported (observed:
`plans/archive/postmortem-frame21-2026-09-16.md`, the table row for the
test sweep). A mechanical edit across many files is a script. The
sweeper type already writes such a script per sweep. The tool is the
part every such script repeats: the file set, the bytes, the line
endings, the report.

## Facts the record stands on

- No tracked file holds a CR byte: `git ls-files --eol` reports `w/lf`
  or `w/none` for every file (observed: 2026-09-17). The CRLF case is a
  file the test writes, not one in the tree.
- `libcst` is not installed in the venv, Python 3.14.2 (observed:
  `pip show libcst`). The transform is a hook: a Python file the caller
  names, with one function. libcst is one way to write that function
  and is not a dependency of this frame. Adding it to the `dev` extra is
  Roman's ruling when a sweep needs it (reasoned: a dependency for a
  path no sweep has used yet is a price with no behaviour).
- `fnmatch` lets `*` cross `/`, treats `**` as two stars, and on Windows
  folds case and swaps separators (observed: R1's probe). Selection uses
  `PurePosixPath(path).full_match(pattern)`: real `**`, case-sensitive
  everywhere.
- `re.sub`'s replacement template eats a backslash: `"C:\temp\new"`
  writes a TAB and a NEWLINE with no error (observed: R5's probe). Both
  Git Bash and PowerShell pass a backslash through intact; the template
  is the hazard, not the shell.
- `samplerepo` writes every file with `write_text`, so its files are
  CRLF, and a fresh `git init` under temp inherits `core.autocrlf=true`
  from Git for Windows (observed: R6's probe). Under `autocrlf=true`,
  `git diff` normalises the working tree and a turned ending shows no
  diff. The tests build their own repository, below.
- `rota/tools/casestatus.py` has no `main`: its `__main__` block parses
  inline (R8). The sweep has `main(argv: list[str], root: Path) -> int`,
  and the block is `raise SystemExit(main(sys.argv[1:], Path.cwd()))`.

## What the sweep is

`rota/tools/sweep.py`, run as `python -m rota.tools.sweep` from the repo
root. One run selects files, decodes all of them, applies one edit to
each, writes only the files that changed, checks its own writes, and
prints the report.

### Arguments

- `--glob <pattern>`, repeatable: matched with
  `PurePosixPath(path).full_match(pattern)` against the tracked file
  list from `git ls-files -z`, deduplicated, with a path that is not a
  file on disk dropped (R10: a deleted file still in the index, a
  conflicted path listed once per stage). An untracked file is never
  selected (reasoned: a mechanical edit is a change to the tree, and an
  untracked file such as another session's prompt file is not the
  tree's).
- `--exclude <pattern>`, repeatable: the same matching, applied after
  the globs. The tool always excludes `rota/tools/sweep.py` and the
  transform file, so a sweep cannot rewrite its own rule (observed: the
  rename script's first run rewrote its own table).
- Exactly one of:
  - `--pattern <regex> --replace <text>`: `re.sub` with `re.MULTILINE`.
    The replacement is literal by default: the tool passes a function
    that returns `<text>`, so a backslash in it is a backslash (R5;
    reasoned: the memory `heredoc-backslash-corruption` counts 23
    strikes on this hazard). `--template` opts into Python's
    backreference syntax for the replacement. A regex that does not
    compile is a usage error, exit 2.
  - `--transform <file.py>`: a Python file that defines
    `transform(text: str, path: str) -> str`, loaded by path with
    `importlib.util.spec_from_file_location` before any file is read; a
    missing file or a missing `transform` is a usage error, exit 2. The
    function receives the text with LF endings and returns LF text. A
    returned text that holds `\r` is rejected: the file is listed under
    `skipped (transform returned CR)` and not written (R4). A hook that
    raises is a handled error, exit 2, and no file is written.
- `--dry`: apply the edit in memory, write nothing, report what would
  change.
- `--diff`: after the writes, print `git diff -- <touched files>` in
  full, for the judgement cases.

### Bytes and line endings

The tool reads and classifies every selected file before the first
write (R7), so a skip is known before anything changes. For each file:

1. Read bytes. A file with a NUL byte in its first 8192 bytes is binary:
   skip it under `skipped (binary)`.
2. Note a UTF-8 BOM by the leading bytes `EF BB BF`, and strip it from
   the bytes the tool works on. Do not decode with `utf-8-sig`: the tool
   must know the file had a BOM to put it back (R3).
3. Classify the ending from counts: `crlf = data.count(b"\r\n")`,
   `lf = data.count(b"\n")`, `cr = data.count(b"\r")`. `LF` when
   `crlf == 0`. `CRLF` when `crlf == lf and cr == crlf`. Otherwise
   `mixed`: skip under `skipped (mixed endings)` (R2; reasoned: the
   frame's test is that a file keeps its own ending, and a mixed file
   has no one ending). A lone `\r` is mixed too.
4. Decode UTF-8 strictly. A file that does not decode is skipped under
   `skipped (not utf-8)`.
5. Normalise `\r\n` to `\n`. Apply the edit. If the text is unchanged,
   the file is untouched.
6. Re-encode with the file's own ending and its BOM if it had one. Write
   bytes. Never `write_text`: on Windows it turns every `\n` into `\r\n`
   and turns an existing `\r\n` into `\r\r\n` (observed: R3's probe,
   `b'ALPHA\r\r\nbeta\r\r\n'`).
7. Read the bytes back and compare them with the bytes the tool meant to
   write. A mismatch prints `write mismatch: <path>` and stops the run
   with exit 3 (R3: a class check passes on a corrupt `\r\r\n` file; a
   byte compare does not).

### The report

Printed in this order, one fact per line:

- `selected <n> files`, then per skip reason `skipped (<reason>) <n>:`
  with the paths.
- `touched <n>:` and one line per file, `<path> <matches> matches
  (<ending>)`. Under `--dry`, `would touch <n>:` instead.
- `unchanged <n>` for selected files the edit did not change.
- `git diff --stat -- <touched files>`, verbatim, when not dry.
- With `--diff`, the full `git diff -- <touched files>` after the stat.

Exit codes, no overlap (R7): 0 when at least one file changed, or
`--dry` reported a change, and nothing was skipped; 1 when nothing
changed and nothing was skipped; 2 for a usage error or a handled error
before any write (no glob, both or neither edit form, a bad regex, a
missing hook, a hook that raises); 3 for a write mismatch, the run
stopped at that file; 4 when the run completed and at least one file was
skipped, whatever else happened. An uncaught exception is Python's 1 and
is a defect.

## Tests

`tests/rota/test_sweep.py`. Each test builds its own repository under
`tmp_path` with this recipe and no other (R6: `gitfixture.make` and
`SampleRepo.edit` write CRLF through `write_text`):

```python
root = tmp_path / "repo"; root.mkdir()
gitfixture.git(root, "init", "-q", "-b", "main")
gitfixture.git(root, "config", "core.autocrlf", "false")
(root / "a.py").write_bytes(b"alpha\r\nbeta\r\n")
gitfixture.git(root, "add", "-A")
gitfixture.git(root, "commit", "-q", "-m", "fixtures")
```

`gitfixture.git` carries `GIT_ENV`, so the commit is deterministic. The
tests call `main(argv, root)` in process; no test runs the tool as a
child.

- A CRLF file and an LF file, both matched and both changed: after the
  sweep, the CRLF file's bytes equal the expected CRLF bytes and the LF
  file's bytes equal the expected LF bytes, compared whole. This is the
  frame's test.
- A file with a UTF-8 BOM keeps its BOM, compared whole.
- A mixed-endings file and a lone-`\r` file are skipped, listed, and
  unchanged; the run exits 4.
- An untracked file matching the glob is not selected.
- `**/*.py` selects a top-level file and a nested one; `*.py` does not
  select a nested one; a path differing only in case is not selected.
- `--replace` with a backslash writes the backslash; `--template` with
  `\1` writes the group.
- `--dry` reports `would touch` and writes nothing: bytes unchanged.
- No match: exit 1, `touched 0`.
- `--transform` with a file that upper-cases one word: the file changes
  and the transform file itself is excluded. A transform that returns
  CRLF text: the file is skipped under `transform returned CR`, its
  bytes unchanged, exit 4.
- A transform that raises: exit 2, no file written.
- `--exclude` removes a matched file.
- A binary file is skipped and listed.
- The self-check: monkeypatch the writer to write `\r\r\n`; the tool
  prints `write mismatch` and exits 3.
- Both edit forms given: exit 2. A regex that does not compile: exit 2.

## Files

- Create `rota/tools/sweep.py`. Relative import of `paths`, an
  `if __name__ == "__main__"` block as above.
- Create `tests/rota/test_sweep.py`.

No other file changes. The two brief lines are in `CLAUDE.md` since
frame 32. The sweeper definition's one-line change, the tool in place
of a hand-written regex script, is the assistant's, after the tool
exists.

## The implementer's pass

One pass. Report in the shape the implementer definition gives. Do not
commit. Ask the map before you grep: `.venv/Scripts/python.exe -m
rota.tools.map fn|table|mode|file <name>`; count the map calls and the
grep calls you made, and report both, because frame 29 closes on that
count. Run `tests/rota/test_sweep.py` first with `-n0`, then the full
suite through the gate once, `.venv/Scripts/python.exe -m
rota.tools.gate`, no `--baseline`, Bash timeout 600000, foreground. The
baseline is at e75e67d with 22 reds; the two `test_screens.py` tests are
known flaky. Do not touch `tests/rota/walks.jsonl` or `You are a standby
peer.md`.
