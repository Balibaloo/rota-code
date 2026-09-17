# The sweep: design record and brief (frame 24, 2026-09-17)

Meta workflow. Written by session 90522022 (rota-99) from the frame's
five lines and the post-mortem of frame 21, change 1. The implementer
builds from the brief. The reviewer reads this record before any code.

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
  `pip show libcst`). The frame's words say "a regex or a libcst
  transform". The transform is a hook: a Python file the caller names,
  with one function. libcst is one way to write that function and is
  not a dependency of this frame. Adding it to the `dev` extra is
  Roman's ruling when a sweep needs it (reasoned: a dependency for a
  path no sweep has used yet is a price with no behaviour).
- `rota/tools/rename_roles.py` is the shape of a prior sweep: a target
  list from `git ls-files`, a substitute function, an exclusion of the
  script itself, a run-once entry point.

## What the sweep is

`rota/tools/sweep.py`, run as `python -m rota.tools.sweep` from the repo
root. One run selects files, applies one edit to each, writes only the
files that changed, and prints the report.

### Arguments

- `--glob <pattern>`, repeatable: matched against the tracked file list
  from `git ls-files -z`, with `fnmatch` on the repo-relative path. An
  untracked file is never selected (reasoned: a mechanical edit is a
  change to the tree, and an untracked file such as another session's
  prompt file is not the tree's).
- Exactly one of:
  - `--pattern <regex> --replace <text>`: `re.sub` with `re.MULTILINE`,
    the replacement in Python's backreference syntax;
  - `--transform <file.py>`: a Python file that defines
    `transform(text: str, path: str) -> str`. The tool loads it by path
    with `importlib`. The function sees the text with LF endings and
    returns the new text with LF endings.
- `--dry`: apply the edit in memory, write nothing, report what would
  change.
- `--diff`: after the writes, print `git diff -- <touched files>` in
  full, for the judgement cases.
- `--exclude <pattern>`, repeatable: `fnmatch` on the path, applied after
  the globs. The tool always excludes `rota/tools/sweep.py` and the
  transform file, so a sweep cannot rewrite its own rule (observed: the
  rename script's first run rewrote its own table).

### Bytes and line endings

For each selected file:

1. Read bytes. A file with a NUL byte in its first 8192 bytes is binary:
   skip it and list it under `skipped (binary)`.
2. Note a UTF-8 BOM. Note the ending: `CRLF` when `\r\n` occurs in the
   bytes, else `LF`. A file with both endings is `mixed`: skip it and
   list it under `skipped (mixed endings)`, because the tool cannot know
   which ending the file's owner wants (reasoned: the frame's test is
   that a file keeps its own ending, and a mixed file has no one
   ending).
3. Decode UTF-8. A file that does not decode is skipped and listed under
   `skipped (not utf-8)`.
4. Normalise `\r\n` to `\n`. Apply the edit. If the text is unchanged,
   the file is untouched.
5. Re-encode with the file's own ending and its BOM if it had one. Write
   bytes. Never `write_text`: on Windows it turns every `\n` into `\r\n`
   (observed: the memory `heredoc-backslash-corruption`, 23 strikes).

### The report

Printed in this order, one fact per line:

- `selected <n> files` and, per skip reason, `skipped (<reason>) <n>:`
  with the paths.
- `touched <n>:` and one line per file, `<path> <matches> matches
  (<ending>)`. Under `--dry`, `would touch <n>:` instead.
- `unchanged <n>` for selected files the edit did not change.
- `git diff --stat -- <touched files>`, verbatim, when not dry.
- With `--diff`, the full `git diff -- <touched files>` after the stat.
- A file whose diff stat shows every line changed is an ending that
  turned. The tool checks this itself: after the write, it reads the
  bytes back and compares the ending to the one it noted. A mismatch
  prints `ending turned: <path>` and exits 3 (reasoned: the check the
  sweeper definition asks the agent to do by eye is the tool's).

Exit codes: 0 when at least one file changed or `--dry` reported a
change; 1 when no file changed and nothing would; 2 for a usage error
(no glob, both or neither edit form, a transform file with no
`transform`); 3 when an ending turned.

## Tests

`tests/rota/test_sweep.py`. Each test builds a throwaway git repository
under `tmp_path` with `rota.testkit.gitfixture` or a direct `git init`,
adds its files, and runs the tool's `main(argv, root)` in process. No
test runs the tool as a child.

- A CRLF file and an LF file, both matched by the glob and both changed
  by the pattern: after the sweep, the CRLF file holds only `\r\n`
  endings and the LF file holds no `\r`, byte for byte except the
  replaced text. This is the frame's test.
- A file with a UTF-8 BOM keeps its BOM.
- A mixed-endings file is skipped and listed, and its bytes are
  unchanged.
- An untracked file matching the glob is not selected.
- `--dry` reports `would touch` and writes nothing: bytes unchanged.
- No match: exit 1, `touched 0`.
- `--transform` with a file that upper-cases one word: the file changes
  and the transform file itself is excluded from the selection.
- `--exclude` removes a matched file.
- A binary file (a NUL byte) is skipped and listed.
- The self-check: a stub that writes the wrong ending makes the tool
  print `ending turned` and exit 3 (monkeypatch the writer).
- A usage error, both edit forms given, exits 2.

## Files

- Create `rota/tools/sweep.py`. Follow `rota/tools/casestatus.py`:
  relative imports for `paths`, an `if __name__ == "__main__"` block.
- Create `tests/rota/test_sweep.py`.

No other file changes. The two brief lines are in `CLAUDE.md` since
frame 32. The sweeper definition's rule "write the script with the Write
tool" stays: the tool takes the script's place for a regex sweep, and a
transform file is written with the Write tool. That one-line change to
the definition is the assistant's, after the tool exists.

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
