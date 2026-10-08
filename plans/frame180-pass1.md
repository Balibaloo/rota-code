# Frame 180, pass 1: the lines door refuses a line with no behaviour

**Record of 2026-10-08, meta workflow. The pass changes a door of the Critic seat, which is the rota workflow.**

**The lines check of `verdicts_emit` now refuses a named line that is a blank line, `pass`, `...`, a comment, an import or a docstring line. s134's real call of night 130 is refused, and the refusal names `echo_json_compact_3` and `import json`.** The same call with the `json.dumps` line for `echo_json_compact_3` lands (observed: `tests/rota/test_verdict_lines.py`, 2026-10-08).

## 1. The change

`rota/roles/api.py`, beside `_line_held`:

- `_shape_kind(text)` gives the kind of a stripped line by its shape: empty, `pass`, `...`, a start of `#`, a start of `import ` or `from ` with no `;`, or a line that is only `"""` or `'''`.
- `_added_kinds(diff_text)` walks the new side of each hunk, the context lines and the added lines. It gives each added line, stripped, with its kind or `None`. It marks a docstring: a triple-quoted string that opens as the first line of a `def` or `class` body, after a header that can span lines. The string's lines up to the closing fence are docstring lines.
- `_held_kinds(line, kinds)` gives the kinds of the added lines that hold one named line, with the same match as `_line_held`: the exact line first, else every added line that contains the part.
- `_pass_lines_check` reads `_added_kinds` in place of `_added_lines`. After the parts of a criterion pass the added-line check, the new check refuses the criterion when every part matches only lines with a kind. The refusal is a `LinesRefusal`, and it records the `verdicts.claim_encodes` offer as the other refusals do.

The words, for s134:

```
the line for echo_json_compact_3, 'import json', is an import, and a blank line, `pass`, `...`, a comment, an import or a docstring line does nothing that a criterion asks for. Copy the added line that does what echo_json_compact_3 says, without the +, and send the pass again. If no added line meets echo_json_compact_3, that is a fail on it: `verdicts.claim_encodes('echo_json_compact_3', encodes=...)` first, as for any fail
```

## 2. The tests

14 new tests in `tests/rota/test_verdict_lines.py`, all green (observed: 2026-10-08):

- `test_s134_pass_naming_import_json_is_refused`: s134's turn 1 call, copied from the `turns` table of `.rota/clickI_night130.db`, opened `mode=ro`. A check confirmed that the copy is a substring of the completion (observed: 2026-10-08). The fixture's diff adds the 14 lines of commit 9a4bddfd verbatim, after the hunk's 3 context lines.
- `test_s134_pass_naming_the_dumps_line_lands`: the same call, with the `json.dumps` line for `echo_json_compact_3`. The diff holds no `raise`, and `json.dumps` raises the `TypeError`.
- `test_a_line_with_no_behaviour_is_refused`, 8 cases on a scripted diff: blank, `pass`, `...`, a comment, `from x import y`, the closing docstring fence, the opening docstring line `"""Do the work.`, and a docstring prose line.
- `test_a_line_that_does_something_lands`, 3 cases: `return total  # the sum of a and one`, an assignment and `if a:`.
- `test_the_s279_comment_alone_is_refused`: s279's added comment line, named alone, is refused.

The blank case names `+`, the added blank line with its plus. A value that is only spaces was refused before as a criterion with no line, and it still is (observed: `test_an_empty_line_is_no_line`).

The scripted passes that carry `lines=` stay green with no change: `judge()` in `rota/testkit/scenes.py` names `return prorate(...)`, `test_arc_seam.py` names `return "tombstoned"`, and `test_delivery.py` and `test_desk_guards.py` name a code line through `a_batch_repo`. The existing tests that name s279's comment line in a value of two parts stay green, because of the rule in section 3.

## 3. Choices the brief left open

- A value of two parts lands when one part does something. Three existing tests name s279's comment beside a code line in one value: `test_the_tolerated_shapes_land[list]`, `[breaks]` and `test_a_value_of_two_lines_lands`. A statement that wraps can start or end on a comment, and the code part names the work (reasoned). So the door refuses a value only when every part has no behaviour.
- A part of 12 characters or more matches every added line that contains it. The door refuses it only when every such line has no behaviour. So a part of a docstring prose line is refused, and a part that is also inside a code line lands.
- An import with a `;` after it holds a second statement, so it is not refused (reasoned: the brief keeps a line that holds a call, whatever else it holds).
- A docstring line is refused whatever it holds, a call-like text included. Text inside a docstring is not code (reasoned).

## 4. What the check cannot see

- A hunk that starts inside a docstring shows no opening fence. Its prose lines read as code and land. Only a bare `"""` or `'''` line in such a hunk is refused.
- A module docstring is not marked. Only a `def` or `class` body opens a docstring here.
- A one-line header such as `class A(B): pass` keeps the header state open until the next line that ends in `:`. A string that opens the body under that line reads as a docstring. No recorded diff has this shape (reasoned).
- A `#` inside a string on a header line hides the colon, and the walk then misses that docstring. This can only admit a line, never refuse code.
- The check still does not see whether a code line meets its criterion. s134's `file.write(out + "\n")` for the ANSI criterion lands, as before.

## 5. The gate

From the worktree at 51678e1f with this change uncommitted (observed: 2026-10-08):

```
suite: 25 failed, 3328 passed, 35 skipped, 17 xfailed, 18 warnings
new reds (0): none
reds gone (0): none
stale (0): none
time: 666.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 51678e1 2026-10-08 04:11
```

The worktree had no baseline, so the gate stored this run and compared nothing. The 25 reds are the known set:

- 7 are in the brief's known list: `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`, `L1-CR-fail-names-its-criterion`, 4 L1-TS cases and `test_map`. The watcher tests of `test_handover.py` are green.
- 18 are the 18 of the stored baseline of 658abb63 that `plans/frame178-pass1.md`, section 4, lists, and no other.

No Critic case changed its prompt, so no case is stale and no re-record ran.
