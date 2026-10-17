# Frame 277, review 2: pass 1b at 3414b5a9, the evaluated interpreter operand

Reviewer: read-only agent, worktree `C:/Users/roman/rota_r277b` at 3414b5a9, 2026-10-17.
Rota workflow throughout. Verdict: not accepted as is. One medium finding and two low findings.
The medium has a cheap fix, and points 1 and 3 hold.

## (a) Verdict on each point

1. Reach: holds for execution. No operand that passes the checks starts a command on this host or reaches `os`. Two low leaks stand (findings 2 and 3).
2. Cost: fails. An operand of two fixed `sys` integers hangs the door, and a string times an integer can allocate gigabytes (finding 1).
3. Certainty: holds. The false operand is admitted, a true operand is refused, and the refusal quotes the seat's own source.

## (b) Findings

1. `rota/roles/api.py:7785` to `7791`, severity medium. CONFIRMED.
   The door evaluates every `BinOp` on fixed attributes. `assert sys.hexversion ** sys.hexversion or path.endswith("/")` ran over 40 seconds in `tests.encode`, and `timeout 40` killed it (12:48:18 to 12:48:58).
   The `except Exception` cannot stop a computation that does not raise.
   `sys.version * sys.hexversion` asks for 80 x 51249904 bytes, about 4.1 GB (PLAUSIBLE by arithmetic, not run).
   `sys.version_info * sys.hexversion` asks for about 256 million tuple slots, about 2 GB.
   A hang in the door stops the seat's API call and the server thread with it.
   Fix: evaluate only when every node is one of `Expression, Compare, Attribute, Name, Load, Constant, Subscript, Slice, Call, Tuple` and the compare operators, so a `BinOp` or `UnaryOp` is never evaluated and the operand is admitted.

2. `rota/roles/api.py:7768` to `7769`, severity low. CONFIRMED.
   The `_` rule covers every `Attribute` node, results included: `sys.platform.__class__ is str`, `sys.version_info.__class__.__mro__` and `sys.implementation.__class__` are all admitted unevaluated.
   A format string bypasses the rule because its field names are a constant, not an `Attribute` node.
   `'{0.__globals__[os]}'.format(platform.system)` and `'{0.__class__.__mro__}'.format(sys.platform)` pass the checks, are evaluated, and are refused.
   A format field can read attributes and items but cannot call, so the leak reads the `os` module's repr and runs nothing.
   Method calls on results also pass: `sys.platform.upper() == 'WIN32'` and `(lambda: sys.platform)()` are evaluated.
   Fix: allow a `Call` only when its `func` is `platform.<name>` from `_interp_platform` with no arguments, and admit every other call.

3. `rota/roles/api.py:7739` to `7745`, severity low. CONFIRMED in part.
   The comment says the door never calls `uname()`, because `uname()` can start a subprocess.
   `platform.release`, `version`, `machine` and `system` each return a field of `uname()`. A probe of `inspect.getsource(platform.release)` shows the `uname` call.
   `platform.release() != ''` passed the checks and was evaluated, so the door calls `uname()`.
   On Windows, `uname()` runs a WMI query, and `_win32_ver` falls back to `cmd /c ver` when WMI raises `OSError` (read in the 3.14.2 source, not run).
   `platform.architecture('C:/Windows/notepad.exe')` passed and was evaluated. On POSIX `architecture(path)` runs `file -b <path>`, and on win32 `_syscmd_file` returns at once.
   `platform.system()` never reaches this door: the process door refuses it first ("reaches the process at line 30 (platform.system(...))").
   Fix: keep only `python_version`, `python_version_tuple` and `python_implementation` in `_interp_platform`, which read `sys` alone.

No comprehension passes: its target is a name other than `sys` or `platform`, so `[x for x in sys.version_info]` and `[sys.platform for _ in sys.version_info]` are admitted unevaluated. A lambda with no argument passes, and it can only read the same fixed attributes.

## (c) Probes

- `C:/Users/roman/rota_r277b/tests/rota/test_zz_review2_probe.py`, untracked, in the worktree only. It calls `tests.encode` through `_encode_or_true` with the `db` fixture of `tests/rota/test_triage_fork.py`. The first run had 16 operands with `import sys`. The second run had 7 operands with `import sys` and `import platform`. Each printed ADMIT, REFUSE or OTHER.
- The same file's `test_hang`, run under `timeout 40`: `sys.hexversion ** sys.hexversion`. It did not return in 40 seconds.
- The same file's `test_false_operand`: `sys.platform != "win32" or path.endswith("/")` returned `{'id': 'ts_or'}`.
- `python -c`: `len(sys.version)` is 80, `sys.hexversion` is 51249904, and `platform.release` calls `uname`.
- The `platform` source in 3.14.2: `architecture`, `_syscmd_file`, `uname`, `_win32_ver`.
- `tests/rota/test_triage_fork.py` in full: 45 passed in 6.54 s. The pass's true, false, raising and quoting tests are green.

## (d) Usage

The harness reports the reviewer's usage. The reviewer's own estimate is about 45k input tokens and 6k output tokens, about 51k in total.
