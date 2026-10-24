# Frame 283, W-D of night 164: how the dropped parameter passed the note door

**Verdict.** The door saw no removed statement because its two readers,
`_lost_statements` and `_owned_statements`, walk the body of a function and
never its `args`, `decorator_list`, `returns` or docstring. Run on the two
texts, `_drop_note` returns `None`. Over nights 155 to 164 this shape landed
once (observed).

## 1. The write

s229, call 11 of 40, turn 3, a span write, not a whole file (observed:
`tool_calls`, `turns`, `.rota/clickI_night164.db`):

```
code.write(path="src/click/utils.py", text='def format_filename(\n    filename: str | bytes | os.PathLike[str] | os.PathLike[bytes],\n) -> str:\n    """Format a filename ...', start=439, end=483)
code.write -> {"path": "src/click/utils.py", "bytes": 21538, "created": false, "written, not committed": ["src/click/utils.py"], "lands with": "code.commit"}
```

The result holds no `dropped` key. Call 12, `code.commit(message="Add single
example to format_filename docstring per principal ruling")`, returned
`{"committed": true, "head_commit": "63c65435..."}`. The old lines read `def
format_filename(`, `filename: ...`, `shorten: bool = False,` and `) -> str:`
(observed: `git show 63c65435^:src/click/utils.py` in
`D:/repos/_AI/sample_repos/clickI`). The text's signature names `filename`
only, and its body is the old body, `if shorten:` included. The tests of
bg_2 read 2 red of 36 at e9bb7c1c before, 5 red at 63c65435, 1 red at s233's
abc65adb, which put the parameter back (observed: `test_runs`). `drop_notes`
holds one row for bg_2, status `restored`, 3 body statements, `if shorten:`
at line 468, `if isinstance(filename, bytes):` at line 473, `return
filename` at line 480, from calls 19, 22 and 24, which wrote the docstring
alone. No row names the parameter.

## 2. The reader

`_drop_note`, `rota/roles/api.py` lines 21767 to 21792, builds the note of a
span write from `_tail_drop` and `_lost_statements(old_lines, start, stop,
text)`, less the heads `_rewritten_heads` reads as rewrites.
`_lost_statements`, lines 21609 to 21740, reads "a compound statement, a
clause, or a `return`, `raise`, `break`, `continue`, `yield`, assignment or
call", its own words.
`_owned_statements`, lines 21806 to 21843, is the second walk, used by
`_rewritten_heads` and by the whole-file door `_whole_lost`. Its docstring:
"A definition is an owner and not a statement." For a def it runs
`walk(s.body, name)` and `continue`, lines 21823 to 21825. Run on the before
text from git and the text of call 11 (observed): `_drop_note(old, 439, 483,
text)` returns `None`, `_lost_statements` `[]`, `_tail_drop` `None`, and
`_owned_statements` lists 7 statements under `format_filename`, lines 470
to 482, none at 439 to 442.

## 3. The gap

Both walks read the statements of a body, the kinds section 2 lists. For a
`FunctionDef` the walk takes the name as the owner and descends into `body`
only. It skips the node's other fields:
`args`, which holds every parameter, annotation and default,
`decorator_list`, `returns`, and the docstring, an `Expr` over a `Constant`.
So the note stays silent on every change of a signature, a decorator or a
return annotation, and the commit door reads only the open notes.

## 4. The count

The night databases hold no `commits` table. The 58 commits come from
`test_runs`, `verdicts` and `batches.head_commit`, all in the click
repository, each parsed with `ast` against its parent for a parameter,
default or decorator held before and not after (observed: `f283_sigcount.py`
in this session's scratchpad):

| Nights | Commits | Signature removals | Landed |
|---|---|---|---|
| 155, 156, 157, 158, 159 | 2, 3, 7, 8, 8 | 0 | |
| 160, 161, 162, 163 | 6, 10, 6, 3 | 0 | |
| 164 | 5 | 1: `format_filename`, parameter `shorten`, 63c65435 | yes |

1 of 58, landed commits only, because a refused write is not in git. No
`drop_notes` row of nights 155 to 164 names a signature part (observed: 15).

## 5. The repair's shape

**A. The signature as one statement.** Owner: the function. Key: the tokens
of the header from the first decorator to the colon. It notes 63c65435. A
normal rename of a parameter loses the old name's token, so the commit is
refused until a write puts it back or a `ledger.log` names the path and the
line, and a changed annotation or default the same way. `_rewritten_heads`
reads the first line alone, `def format_filename(`, which the write kept, so
pass 8b would silence the note unless the rule reads the whole header.

**B. Each parameter and each decorator as a statement.** Owner: the
function. Key from the node, `arg.arg` with its default, as an assignment
keys on its targets today. It notes 63c65435 with `shorten: bool = False,`
at line 441, the form the body notes use. A rename is refused the same way,
until noted, because the old key is gone. A one-line signature works too.

The page favours B: it names the one line the Developer dropped, it reuses
the pair-by-place rewrite rule unchanged, and it leaves the other parameters
alone. Both refuse a rename until the Developer names it, today's rule for a
body statement, and a renamed click parameter breaks keyword callers as a
removal does. The change sits in the two walks, so both doors move together.

Usage: about 62k on the harness line against 60k, Opus reader, read-only.
