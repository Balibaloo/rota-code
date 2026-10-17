# Frame 277, review 3: pass 1c at 8b290211, the node walk before the evaluation

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_r277c` at
8b290211 (observed: 2026-10-17). Rota workflow throughout.

Verdict: accepted. Review 2's three findings are closed. No high or medium
finding stands. Three low findings stand, and two of them are outside the
diff.

## (a) The verdict on each point

1. CONFIRMED. Review 2's three probes now admit the body at once. No operand that the walk allows reaches past a read. Two long chains cost more than a second, from older loops (findings 1 and 2).
2. CONFIRMED. The test file passes 51 of 51 at 8b290211. With the 3414b5a9 door swapped in, 4 new cases refuse and the arithmetic test hangs.
3. CONFIRMED. The diff removes 3 lines, the three lines of `_interp_platform`. The 38 added lines hold no f-string, no CR and no tab.

## Point 1, review 2's findings and the walk

Review 2's probes, rerun through the real door (`T._encode_or_true`):

| operand | result | time |
|---|---|---|
| `sys.hexversion ** sys.hexversion or x` | admitted | 0.20 s |
| `'{0.__globals__[os]}'.format(platform.system) or x` | admitted | 0.01 s |
| `platform.release() == "10" or x` | admitted | 0.02 s |
| `platform.system() or x` | refused by the process door, not this door | 0.00 s |

Operands that use only the nodes the walk allows:

| operand | result | time |
|---|---|---|
| `sys.version[0][0][0] == "3" or x` | refused, true | 0.05 s |
| `sys.version_info[0] == sys.version[0][0] or x` | admitted, false | 0.01 s |
| `sys.version` with 2000 `[0]` | refused, true | 0.12 s |
| `sys.version in '<1e6 a>' or x` | admitted, false | 0.05 s |
| `sys.platform in '<1e6 a>win32' or x` | refused, true | 0.08 s |
| `sys.hexversion in (0..9999)` | admitted, false | 0.40 s |
| `sys.hexversion in (0..9999, hexversion)` | refused, true | 0.24 s |
| `x or ` 10000 `sys.maxsize` joined by `and` | refused, true | 2.63 s |
| `x or ... or x`, 3000 names | admitted | 0.99 s |
| `x or ... or x`, 10000 names | admitted | 10.02 s |
| `x == 0 or ... or x == 2999` | admitted | 2.68 s |
| `x or ` 1000 `not ` before `sys.maxsize` | refused, true | 0.04 s |
| `x or ` 5000 `sys.maxsize` joined by `<` | admitted, false | 1.06 s |
| `x or sys.implementation.name.upper` | refused, true | 0.01 s |
| `x or sys.version_info[...]` | admitted, raises | 0.01 s |
| `x or (sys.maxsize,) == (1,)` | admitted, false | 0.01 s |

No operand reaches past a read. The only call the walk allows is a fixed
`platform` function with no argument. Every attribute is non-underscore on
a `str`, `int`, struct sequence or namespace. The walk and the evaluation
are linear in the operand. The bodies over one second are 50 KB to 160 KB.
Their cost comes from two quadratic loops that 8b290211 did not touch
(findings 1 and 2).

## Point 2, the right bodies

1. At 8b290211, `tests/rota/test_triage_fork.py` passes 51 of 51 in 5.3 s. The s256 and s198 refusals and the admit shapes of passes 1 and 1b are in that file.
2. I exported 8b290211 with `git archive` and put `git show 3414b5a9:rota/roles/api.py` in the export. Then I ran the same file with `-n0`.
3. With `-k "not arithmetic"`: 4 failed, 46 passed. The 4 failures are the 4 cases of `test_an_operand_the_door_does_not_read_is_admitted`. The old door evaluated each operand, found it true, and refused it. `platform.release()` returns "10" on this host.
4. `test_a_fixed_platform_call_is_refused` passes on both doors. It guards the one call the walk keeps.
5. The full file with the old door ran past 600 s and did not finish. The arithmetic test computed the power. I stopped the run by its PID.

## Point 3, byte for byte

The removed lines are exactly the three lines of the old
`_interp_platform` set. The added lines are comments, the new set, the
node tuple, `_only_reads` and its call. No added line holds `f"` or `f'`.
The file holds no CR, and no added line holds a tab.

## (b) Findings

1. `rota/roles/api.py:7810`, low, outside the diff (from 3414b5a9). CONFIRMED: an `and` chain of 10000 `sys.maxsize` took 2.63 s. The cost is the nested `any(f is n for f in fixed)` over every name, which is quadratic (reasoned: 10000 names times 10000 attributes). Fix: build `fixed` as a set, because AST nodes hash by identity, and test `n in fixed`.
2. `rota/roles/api.py:7857`, low, outside the diff (from 7b48a630). CONFIRMED: an `or` of 10000 names took 10.02 s, and 3000 compares took 2.68 s. The pairwise `_complementary` loop is quadratic. Fix: key each single-op compare by its operands' dump and look up only its opposite.
3. `tests/rota/test_triage_fork.py:428`, low. CONFIRMED: against the 3414b5a9 door, the timed test ran past 600 s and did not fail. The test reads the clock after the call returns, so a regression hangs the gate. Fix: run the door call in a daemon thread and fail when the join passes five seconds.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/eefbf293-6e8b-4a35-91c4-b3f1fed91a11/scratchpad/f277/r3/probe3.py`. It runs operands through `T._s256_with` and `T._encode_or_true` on a fresh database and prints the result and the time. Mode `r2` reruns review 2's probes. Mode `walk` runs the walk-allowed operands. Run it from the worktree root.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/eefbf293-6e8b-4a35-91c4-b3f1fed91a11/scratchpad/f277/r3/old/`. This is a `git archive` export of 8b290211 with 3414b5a9's `rota/roles/api.py`. I ran `pytest tests/rota/test_triage_fork.py -n0 -k "not arithmetic" --tb=no` there.
- A `python -c` probe read the bytes of `git show 8b290211 -- rota/roles/api.py`. It counted the removed and added lines, the CR, the tabs and the f-strings.
- `git blame` on lines 7810 and 7857 named the commits of findings 1 and 2.
- Review 2's worktree `C:/Users/roman/rota_r277b` is gone, so I wrote the probes again. The file `r1/probe1.py` is review 1's probe, and I read only its database set-up.

## (d) Usage

The harness line carries the agent's tokens. The reviewer cannot read its own count.
