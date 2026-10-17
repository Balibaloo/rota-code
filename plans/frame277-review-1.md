# Frame 277, review 1: pass 1 at 7b48a630, the encode door on an `or` that cannot fail

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r277` at 7b48a630, 2026-10-17. Rota workflow.

Verdict: **accepted with findings.** 0 high, 1 medium, 3 low. The door fires on the two night shapes and on nothing else in the records. The medium is a class of right body that the interpreter shape refuses. No night body holds that class.

## (a) Verdict on each point

1. False fires: CONFIRMED with one exception. Eight of the brief's ten bodies are admitted. `sys.platform == "win32" or path.endswith("/")` is refused (finding 1).
2. The deviation: CONFIRMED allowed. No ruling forbids the refusal of one tautological `or` beside real asserts. The step lands: s256's body without the operand is admitted.
3. The count: CONFIRMED. The script prints 4 of 1953, 0 of 156 red bodies, 0 of 821 cassette bodies.
4. Byte for byte: CONFIRMED. The api.py hunk has 79 added lines and 0 removed lines. The old texts are unchanged.
5. The tests: CONFIRMED. At the parent's api.py, the five red tests fail with `DID NOT RAISE`, not at an import. Four of point 1's shapes have no admit test (finding 4).

### Point 1, detail

Probe `probe1.py` sends each body through `tests.encode` on a fresh database, built on `S256_BODY` with each name bound.

- Admitted: `"Python" in ... or "python" in ...`; `exit_code == 0 or exception is None`; `sys.version_info >= (3, 8) and ...`; `x == 1 or x == 2`; `a is None or b is None`; `out or not err`; `result.output.strip() or sys.stdout.getvalue()`.
- `sys = make()` in the body: admitted. The local binding puts `sys` in `_bound`, so the interpreter shape returns False.
- `from sys import version_info` with `assert ok or version_info[0] == 3`: admitted. The operand holds no `sys` or `platform` name, so the shape does not look at it. This is a miss and not a false fire. No night body has the shape.
- Refused: `sys.platform == "win32" or path.endswith("/")` and `sys.platform != "win32" or path.endswith("/")`. See finding 1.

### Point 2, detail

- Frame 147 is about `assert False` under `try/except` that the constant rule refuses. Its lesson is "a false refusal loses a repair". It does not rule on an `or` beside a real assert.
- `rota/DECISIONS.md` line 945 onward sets the door's line: a refusal must be "certain independent of what the criterion means". A true interpreter operand or a pair of opposites inside an `or` is certain. So the any-assert rule fits that line.
- Frame 273's "a real assert beside an `or True` is admitted" was a narrowness choice in that pass, not a ruling. That rule and its test are unchanged.
- The step: probe case `s256 operand removed` (turn 4's body with `assert "Python" in result.output`) is admitted. Probe case `taut beside 3 real` (the tautology beside three real asserts) is refused with the new text.

### Point 3, detail

- "Ran red" in `count277.py`: the body's test id has a `test_runs` row with `result != 'pass'`, so `error` counts too. The output of that row must also quote the first line of one of the body's asserts.
- A body accepted by the principal is not in the right set. The script does not compute that set. The stronger fact is that the 4 fires are the 2 named tests, so 0 of the other 1949 distinct bodies fire.
- The script copies the predicate. I compared the copy with the hunk line by line. It matches.

### Point 5, detail

- The parent copy of the tree is `git archive 7b48a630` with `git show 7b48a630^:rota/roles/api.py` over it, in the probe directory. Result: `5 failed, 28 passed`, the five new red tests, each `DID NOT RAISE <class 'ValueError'>`.
- At 7b48a630 in the worktree: `33 passed`.

## (b) Findings

1. `rota/roles/api.py:7746-7762`, `_reads_interpreter_alone`. Severity **medium**. CONFIRMED. The shape refuses an interpreter operand whatever its value. `assert sys.platform != "win32" or path.endswith("/")` can fail on this Windows host, and the door refuses it. `assert x or sys.version_info[0] == 2` is refused too. The text then says "cannot fail", which is false for those bodies. `rota/DECISIONS.md` requires a refusal that is certain. The brief's `== "win32"` form is true on this host, so its refusal is right on this host only. 0 of 1953 night bodies hold the class.
   Fix: evaluate the operand in a namespace that holds only `sys`, `platform` and pure builtins, and fire only when the result is truthy.
2. `rota/roles/api.py:7759`, `hasattr(_builtins, n.id)`. Severity **low**. CONFIRMED. Every builtin passes, including `open` and `input`. `assert "Python" in result.output or sys.version in open("out.log").read()` is refused, but the file can hold the call's output.
   Fix: replace `hasattr(_builtins, ...)` with a short set of pure builtins such as `len`, `str`, `int`, `tuple`, `bool`.
3. `rota/roles/api.py:7750-7760`, the name `platform`. Severity **low**. CONFIRMED. `platform` passes with no check that it is the module. `from click import utils as platform` with `assert ok or platform == "linux"` is refused. The import alias is not in `_bound`, because `_bound` reads `Name` stores, arguments and definitions only. The same holds for `sys` bound by an import alias.
   Fix: add the `asname` or `name` of every `Import` and `ImportFrom` alias to `_bound`, except `import sys` and `import platform`.
4. `tests/rota/test_triage_fork.py:345-357`, the admit test. Severity **low**. CONFIRMED by reading. The parametrised admit test lacks `x == 1 or x == 2`, `a is None or b is None`, `out or not err`, a body that binds `sys` locally and a body with `from sys import version_info`. Each is admitted today (probe 1), but no test pins it.
   Fix: add the five bodies to the admit test with their names bound.

Outside the points:

5. `rota/roles/api.py:7779` and `:7785`. Severity **low**. CONFIRMED. `_ast.unparse` rewrites the operand. In the probe the line quotes `"out.log"` and the operand quotes `'out.log'`. So the quoted operand is not a substring of the quoted line, and a seat that searches its body for the operand text does not find it.
   Fix: quote the operand with `_ast.get_source_segment(body, v)` and use `unparse` only as the fallback.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/eefbf293-6e8b-4a35-91c4-b3f1fed91a11/scratchpad/f277/r1/`.

- `probe1.py`: run from the worktree root. It sends 16 bodies through `tests.encode` with the test file's `_encode_or_true`, each on a fresh database. It covers point 1, point 2 and findings 1 to 3 and 5.
- `count277.py` (the pass's script, one level up): run unchanged. It printed 4115 calls, 1953 distinct bodies, 4 fires, 156 red, 0 refused, 3747 cassette calls, 821 bodies, 0 fires.
- `parent/`: an archive of the tree at 7b48a630 with the parent's `api.py`. The command ran `pytest tests/rota/test_triage_fork.py` there and gave `5 failed, 28 passed`.
- In the worktree: `pytest tests/rota/test_triage_fork.py` gave `33 passed`. `git show 7b48a630` with `grep` showed 0 removed lines and only the new f-strings.
- The full gate did not run. No point needed it.

## (d) Usage

An estimate from this context, not the harness line: about 75k input tokens, about 10k output tokens, about 85k total. The harness line is the authority.
