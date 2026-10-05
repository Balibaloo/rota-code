# Frame 136, a span write removes a file's import lines: the read and the design

Rota workflow, unless a line says otherwise. Pass 0 of frame 136, an agent on Opus, 2026-10-05.
The agent read `.rota/clickI_night113.db` to `.rota/clickI_night120.db` with `mode=ro`, the
clickI clone `D:/repos/_AI/sample_repos/clickI`, and `code_write` at `rota/roles/api.py:8995-10241`.
No model was called. The scripts are in the session scratchpad `f136/`.

## 1. The cause

**Confirmed, with two corrections. The Developer meant an insert, and no text in its prompt says what a span does. The door that checks for a name the text still uses runs on whole-file writes only.**

- s227, turn 4, wrote "`sys` is not imported. That's the problem." and "I will: 1. Add `import sys` near the other imports." The same reply sent `code.write(path='src/click/decorators.py', text='import sys\n', start=0, end=5)`. The result was `OK code.write -> {"path": "src/click/decorators.py", "bytes": 22027, ...}` (observed: turns of s227, 2026-10-05).
- The seat meant an insert (reasoned: "add ... near the other imports"). No reading makes 0..5 an insert. The code replaces lines `start` to `end - 1`, and only `start == end` inserts (observed: `api.py:9035-9039`, `9516-9520`).
- The seat's prompt shows the tool as one line, `TOOL: code.write(path, text, start=0, end=-1)`. It never says that a span replaces its lines. The `code.source` block numbers no lines. It gives `defs` as `[start, end)` and says so (observed: the system and user text of s227, turns 1 and 2, 2026-10-05).
- Lines 0 to 4 held `from __future__ import annotations`, a blank, `import inspect`, `import typing as t` and `from functools import update_wrapper` (observed: the turn-2 `code.source` block).
- s227 sent the same write again at turns 6, 7 and 9, each time inside a replay of its own earlier reply. The runner ran the first call before the copied result, so each landed: 21940, 21837 and 21689 bytes (observed: the prompts of turns 7, 8, 10).
- **Correction 1.** These replays, not s228, removed the imports from `.core`, `.globals` and `.utils`. They stayed uncommitted, and s228's commit cfed9d8e5d carried them (observed: `git show a3352d90e3` still holds the `.core` lines, and the replay below matches every byte count). `plans/night120-read.md` section 2 item 10 says s228 removed them.
- **The nearest repair.** At turn 10 s227 sent the whole original header with `import sys` as its first line, `start=0, end=8`. The compile door refused it 3 times: `src/click/decorators.py is not valid Python (from __future__ imports must occur at the beginning of the file, line 1 in code.source numbering)`. The refusal names no step. The seat then wrote "The harness rejects any code.write that moves imports around" and sent `schedule.reask` (observed: s227 turns 10 to 15). With the `__future__` line moved first, that write leaves no name unbound, and `import click` succeeds on a copy of a3352d90e3 (observed: `near.py`, 2026-10-05).
- **Correction 2.** Night 113 met the same sign. s146, turn 4, sent `code.write(path='src/click/utils.py', text='from . import click\n', start=0, end=15)`, and 537e5f2281 took 37 of 37 tests to `error`. `plans/night113-read.md` says s146 "added `from . import click` at line 1". The write replaced 15 header lines (observed: s146 turns 4 and 5, `test_runs`).

## 2. The counts

- Nights 113 to 120: 91 landed `code.write` calls on `.py` files, all spans. The replay rebuilt the pre-state of 89, each matched to the byte count in the result. 2 stay unknown, both in night 115's s130 (observed: `spans.py`, 2026-10-05).
- **The sign: 5 of 89 landed writes leave a name unbound that the file bound before and still uses.** s227 turns 4, 6, 7, 9 (night 120) and s146 turn 4 (night 113). All 5 were harmful: the commits that carried them show 43 of 43 and 37 of 37 `error` (observed: `test_runs`).
- Batches given up after such a write: 2 in 8 nights. Night 113 bg_1 ended `attempts=3 quarantined=1`, and the cycle fired at attempt 6 (copied: `plans/night113-read.md` section 3). Night 120 bg_3 is the same, 1 of 3 batches.
- Night 120, s228 to s232: the drops door refused 22 writes, s228 1, s229 4, s230 14, s232 3 (observed: the runners' end accounts). Every refusal paired with its call, 7 of 7, met a header text with no `def` or `class`, sent with `end=-1`. s230 turn 8 sent 15 writes, 11 of them header texts.
- The drops refusal names `start=0, end=0` for an import. The seat sent that insert next in 2 of 2 cases, s228 turn 3 and s229 turn 6, and both landed (observed). A named call moves this seat.
- That insert does not repair. s230 turn 6's correct header at 0..0 above the broken one still fails `AttributeError: type object 'typing.TypeVar' has no attribute 'TypeVar'`. The same text at `start=0, end=9` imports clean, and it leaves `sys` unbound (observed: `near.py`).
- s231's 3 refusals came from the fence: `reaches the dynamic at line 220 (from importlib.metadata import ...)`. The file holds `import importlib.metadata` at line 498, and the fence keys a reach by its spelling, so the refusal is false (observed: `fence.reaches`, `git show 128f6e4967`).
- Wall 5. The revert door at `api.py:10413-10429` runs `git diff --quiet HEAD~1` and `git diff --quiet HEAD`. It reads no test run. "The tests pass both ways" comes from clickI night 30, a flip of one newline. s230's 0..9 write had put back the bytes of cfed9d8e5d (21754), HEAD was s229's 128f6e4967, and both were 43 of 43 `error`. The sentence is false, and "your last commit" is false for s232 too (observed).

## 3. The doors on a span write, in order

1. No batch. 2. The path escapes the worktree. 3. The path is a parameter name. 4. `start` with no `end`.
5. The file does not exist. 6. The span is out of range. 7. A blank span that leaves a blank file is an empty write.
8. A boundary falls inside a statement (`_cut`). 9. An insert above a `__future__` import. 10. An insert on a docstring.
11. The boundaries sit in two blocks. 12. The merge, and the `dropped` note, which never refuses.
13. A manifest file. 14. A root module beside a src package. 15. A root module named like the standard library.
16. Parse and compile, after the broken-string repair. 17. A name defined twice in the file. 18. A name defined in another module.
19. The fence, against the old file. 20. A test file. 21. The main guard and what it calls. 22. `input()` at module level.
23. An `input()` reader that a batch test calls. 24. A user-acquire criterion with a niladic function.
25. The drops door: `gone`, definitions that tests, criteria or other files import, runs on spans. `used`, old top-level names the text still loads and binds nowhere, runs only `if not span and not star` (`api.py:10097`).
26. `_changed_unnamed_defs`. 27. The own-package cycle, `from click import` at level 0 only. 28. A missing module and a module in the wrong folder. 29. An unchanged text.

Door 25's `used` should have met s227 turn 4. It judges the merged tree, so it holds for a span unchanged. Commit 791da68 (2026-09-30) built it for one whole-file case, ACT-DV-edit-inside-the-function, and gated it to whole files. On the merged tree of turn 4 it gives `inspect`, `t`, `update_wrapper` (observed: `spans.py`).

## 4. The candidates against the turns

- (a) A door on the span path: s227 turn 4, its three replays and s146 turn 4 are refused. s228's 0..15 binds `t = TypeVar` and passes, because `t` was already gone. The door prevents a break and cannot repair one.
- (b) Tool text: no change at the turn. The signature line is in the system prompt, and the cassette key covers it (copied: `runner.py:263-267`). Every recorded case with a Developer seat goes stale, 18 `DV` cases and more. Its effect on s227 is unmeasured.
- (c) A repair route in the drops refusal: s230 turn 6 gets the header span `start=0, end=9` in place of 0..0, and frame 114 plans a quote of the lines a batch changed outside definitions. Without it, the attempt-6 header texts keep meeting a step that lands and does not repair.
- (d) A step in the `__future__` compile refusal: s227 turn 10's restore lands at turn 11, in the session that made the break.

## 5. The design

Recommended: (a) and (d) in this frame, and the dry-run below. (c) goes with frame 114, because both change the drops refusal. (b) waits for an interview.

**The predicate (a).** For a span write on a `.py` file whose old text parses, with no star import in the merged tree: `U = (set(_top_binds(old)) - _bound_anywhere(merged) - set(dir(builtins))) & {Load names of merged}`. A non-empty `U` refuses. It is ast only, door 25's `used` with the gate removed. The span refusal runs after door 27, so that every other door has judged the call first.

**The dry-run.** A refusal names a call only when the doors admit that exact call (the rule of frame 135). The body of `code_write` moves to `_code_write(ctx, path, text, start, end, *, dry)`. `code_write` keeps its signature and docstring, so the prompt does not move. A dry run raises like the real one, returns before any write or unlink, and builds no offers. `_admits(...)` is a call of `_code_write(..., dry=True)` that returns False on `ValueError`. Each refusal below tests its call through `_admits` and names it only on True. Otherwise it states the fact and names no call.

**A1**, when the text binds none of the names that the removed lines bind. The insert point `p` is `start`, moved below the leading `__future__` imports and the module docstring when `start` sits at or above them:

> start=0, end=5 removes 'import inspect', 'import typing as t' and 'from functools import update_wrapper', and the rest of src/click/decorators.py still uses inspect, t and update_wrapper. To add your text and keep every line, send start=1, end=1.

Next call: `code.write(path='src/click/decorators.py', text='import sys\n', start=1, end=1)`. Proof, traced on the code and to be held by a test (reasoned): line 1 is the blank after the `__future__` import, so `_cut` gives None (door 8). The future door passes, because 1 > `_lo` 0 (door 9). No docstring starts at line 1 (door 10). `start == stop` skips door 11. The merged file compiles, defines nothing twice, keeps every binding, and changes no definition. Door 27 reads `import sys` only. For s146 the same offer, `from . import click` at line 1, is a cycle. Today's door 27 admits it. After frame 114's relative check lands, `_admits` fails and A1 names no call.

**A2**, when the text binds some of those names, a replace:

> start=0, end=9 removes 'import sys', and the rest of src/click/decorators.py still uses sys. To keep it, put that line in your text below any `from __future__` line, and send start=0, end=9 again.

The door builds that text, with the quoted lines after the text's `__future__` lines and docstring, and names the step only when `_admits` passes. On s230 turn 6's header at 0..9 with `import sys` added, `U` is empty and `import click` succeeds (observed: `near.py`).

**D**, the compile refusal when the text holds a `__future__` import below another statement and `start` is 0 or only `__future__` lines precede it:

> Python takes 'from __future__ import annotations' only above every other statement, and your text puts 'import sys' above it. Send the same call with that line first in text.

Proof: the door moves the text's `__future__` lines to its top and names the step only when `_admits` passes. On s227 turn 10, `start=0, end=8`, the moved text compiles, `U` is empty, and `import click` succeeds (observed: `near.py`).

**C, for frame 114**, when the text holds no `def` or `class` and the span covers every top-level definition. The header span is the seat's `start` to the first top-level definition, decorators included:

> Your text holds no def or class, and start=0, end=-1 replaces every definition of src/click/decorators.py. To replace only the header above pass_context, send start=0, end=9.

It names the call only when `_admits` passes. When `U` blocks it, the step carries A2's clause. On s230 turn 6 that clause is "with 'import sys' in your text below the `from __future__` line".

**False positives.** 0 of 84 silent landed writes would be refused, and the 5 hits were harmful (section 2). No whole-file write landed on these nights. So the removal of `not span` is the only change to a path that landed writes.

**Tests** (`tests/rota/test_desk_guards.py`, with a trimmed `decorators.py` header and two definitions):

1. s227's call is refused with A1's text, and the named call returns OK and keeps every line.
2. The same write with a text that binds `t` again passes, so a replace of the header is free.
3. A2: a header span without `import sys` is refused, and the named text is admitted.
4. D: s227 turn 10's text gets D's step, and the reordered call is admitted.
5. A star import in the merged file and a name bound only as a builtin pass silently.
6. When `_admits` fails, the refusal holds no `send` and no call.

**Stale cases.** A1, A2 and D change result text only on the paths they refuse. The qwen3:8b recordings hold span writes in L1-DV-fix-the-code-not-the-test (`pricing.py` 16..-1, an append), the formatting cases (11..-1 appends, one 0..11) and L1-DV-read-the-map-not-the-whole-file (`termui.py` 0..248). The appends remove no line. The other two were not replayed (reasoned: the fixtures were not rebuilt). Expected stale: 0 to 2, and the gate's stale line decides. (b) would make every case with a Developer seat stale.

**The measure.** The mechanism: the door refuses A1's shape, and every named call passes `_admits`, which the 6 tests hold. A span door is proved by unit tests and on a night, not by an L1 case (copied: `plans/operating-facts.md`, frame 92). The ratio: landed span writes with the sign fall from 5 of 89 on nights 113 to 120. After an A1, A2 or D refusal, the session's next write is the named call in at least 1 of 2, against 2 of 2 for the drops door's named insert on night 120. The residue: a session that still lands the sign is read, and the frame closes when the cause is not the predicate, for example a star import.

**Price.** One implementer pass on Opus, cold, one file and 6 tests and a gate: about 150k (anchors 74k to 217k). One diff review: about 70k. A walk: one night. C adds about 30k to frame 114.

**As built, pass 1 (2026-10-05).** The coordinator ruled on section 7: the dry run is accepted, A2 and D may refuse in a row, C goes to frame 114, and no tool text moves.

- The predicate also refuses a span that removes a `from __future__` import whose features the merged file no longer holds. Over the 89 landed writes, 2 removed such a line, s146 and s227, and both are among the 5 hits (observed: `spans.py`, 2026-10-05).
- `_span_lost` in `api.py` computes `U` and the removed `__future__` imports. Its refusal, `_span_lost_refusal`, runs after door 27. A1 applies when the text, parsed alone, binds none of the names that the removed statements bind. Otherwise A2 applies.
- A1 on s227's call now quotes the `__future__` line too: "start=0, end=5 removes 'from __future__ import annotations', 'import inspect', 'import typing as t' and 'from functools import update_wrapper', and the rest of src/click/decorators.py still uses inspect, t and update_wrapper. To add your text and keep every line, send start=1, end=1."
- A removed `__future__` import alone gives the fact "... and the rest of <path> runs under that `from __future__` import." A2 with a removed `__future__` line says "put those lines at the top of your text, the `from __future__` line first".
- D replaces the bare compile refusal when `_future_order` finds the text's `__future__` import below another statement. When `_admits` fails, D keeps its first sentence and names no call.
- Pass 2 (2026-10-05), after the review of 08caa8d. A2 names a call only when every quoted statement is an import. The built text keeps the text's docstring and `from __future__` lines first, then puts the removed `__future__` lines and the removed imports, then the rest of the text. A removed assignment, def or class gets the fact alone, because compile is not import: `R = t.TypeVar("R")` landed above `import typing as t`. A quote starts at a decorator. A blank text gets the fact alone. A1's insert sits below a `#!` line and a coding comment. D fires only when `start` is at or above the file's first statement that is not a docstring or a `__future__` import. `_admits` treats only `ValueError` as a refusal. Any other exception is logged to `rota.roles.api` and names no call.
- A2's sentence as built: "To keep {it|them}, put {that line|those lines} at the top of your text, below any `from __future__` line, and send start=…, end=… again."
- A dry run returns `{}` before the disk, and an empty write in a dry run removes nothing. A refusal inside a dry run is the fact alone, so it starts no second dry run. 8 tests in `tests/rota/test_desk_guards.py` hold this, and one of them compares `ctx` and the worktree around `_admits`.

## 6. What the design does not cover

- s228's `t = TypeVar`: a wrong binding of an old name passes the predicate.
- The repeat of a seat's own earlier reply, which re-ran three writes in s227 (frame 117's sign).
- s231's fence refusal for a spelling of an import that the file already holds.
- Wall 5, the revert door's sentence. It needs the runs of HEAD and HEAD~1, and one api test.
- The relative-import cycle of s146, which frame 114 covers. A1 must not offer an insert that the new cycle check refuses, and the dry-run holds that.
- A text cut at the output budget, s230 turns 1 to 3 (frame 121).
- An import under a top-level `try:` or `if TYPE_CHECKING:` binds no name for `_top_binds`. A span that removes such a block is not refused (observed: the review of 08caa8d, point 6, 2026-10-05). The predicate does not widen in pass 2.
- A2 restores only the imports that the span removes. When an earlier write already removed another import, the A2 step lands and the file still fails at import. The reviewer's replay of s227 turns 6, 7 and 9 shows `NameError: name 't' is not defined` after the step (observed: `review136/variants.py` on the main checkout, 2026-10-05).

## 7. Open points for the judge

1. Is the dry-run worth its size? `_code_write` moves about 1,250 lines under a new name and does not change their indentation. The cheaper form re-runs only doors 16, 17, 25 and 27 on the offered call. It proves less, because the order of doors can change.
2. A2 tells the seat to put lines "below any `from __future__` line". The seat may put them elsewhere, and D then answers. Accept two refusals in that case, or make A2 send the whole text?
3. Does C go to frame 114 or stay here? Both edit the last sentence of the drops refusal.
4. (b) needs an interview of s227 turn 4, which asks what `end=5` meant, before any tool text moves. The night holds the GPU now.
5. `plans/night120-read.md` section 2 item 10 and `plans/night113-read.md` section 3 carry the two corrections of section 1. This pass did not edit them.
