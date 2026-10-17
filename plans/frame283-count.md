# Frame 283, the count of the dropped-note door over nights 140 to 154

Agent: Opus, read-only, 2026-10-17. Door: `_open_notes`, `_put_note`,
`_unread_drop_refusal`, `_close_logged_notes` and the note path of
`_code_write` in `rota/roles/api.py` at 7471569c. The file has no diff
between 7471569c and HEAD (observed: `git diff --stat`, 2026-10-17).
Scripts: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/count/`
(`count3.py` is the list, `sim.py` is the door simulation, `judge.py` is the
evidence per session; the outputs are `count3.out`, `sim.out` and `judge.out`).

## Result

- N = 32 sessions with a `dropped` note and a later landed commit
  (observed: `count3.out`).
- a = 21 of 32: the door at 7471569c refuses the first commit after the note.
- b = 20 of 21: the refusal is right, because the removal is lost.
- One wrong refusal: night 149, s192. The note is in reply 15. The commit
  39f9365f is in reply 16 (reasoned, see the table).
- Both known cases are in the list and are refused: night 154 s340
  (1e9925fc) and night 154 s388 (a90c7495).

## Step 1. The reconciliation

- Review 1's probe (`f283r1/probe_exposure2.py`) matches the JSON form
  `"dropped": "This write` anywhere in `user`. It takes a landed commit
  from the JSON form `code.commit -> {"committed": true, "head_commit":`
  in a turn strictly after the note turn. It found 18 (observed: rerun,
  2026-10-17).
- Pass 2's `count2.py` matches the rendered form `[dropped]` followed by
  `This write` on the next line, in the last 6000 characters of `user`. It
  takes the commit from the JSON `OK code.commit -> {...}` in the same turn
  or later. It found 9 (observed: `count2.out`).
- Why the lists differ: a `code.write` result is JSON when it is short and
  rendered as `key: value` lines with a `[dropped]` block when it is long
  (observed: s453 of night 146 has a JSON note in reply 7 and a rendered
  note in reply 12). Each script reads one form only. Review 1 also drops a
  commit in the same reply as the note, and pass 2 can miss a note that is
  more than 6000 characters from the end. The one shared session is s453 of
  night 146, which has both forms.
- `count3.py` reads both forms in each result block of the previous reply's
  calls (the text after the first `\nTOOL:` line). A sha counts at its first
  appearance, because later turns repeat the commit result. A commit in the
  same reply counts when its result comes after the noting write's result.

Two note shapes exist: "This write removes N statements ... `x` at line n"
and the tail note "This write drops N lines that came after `a`, from `b`."
(observed: `judge.out`).

## Step 2. The judgement per session

Method, and its limit. `sim.py` applies the door's rules: the note path is
in the commit; a later write on the path holds every dropped statement
(restore); an OK `ledger.log` names the path and a dropped statement
(ledger). The base-commit rule needs the batch's base tree, which this read
did not open. The base column is decided by hand from the statement text:
a statement that names the batch's own feature (`show_python`,
`callback=callback`, the JSON echo lines, single-quoted `'--version'`) is a
batch addition (reasoned). The click 8.5.0 copy in `.venv` was tried as a
base proxy and rejected, because the fixture's click is a different version
(observed: `sim.out` marks `echo(version_msg)` as absent). Meant or lost is
decided from the note text and, for s192, s228 and s283, from the noting
write's text. The full turns of every session were not read inside the cap.

| Night | Session | Note reply | Commit reply, sha | Refuse | Rule | Removal | Verdict |
|---|---|---|---|---|---|---|---|
| 141 | s197 | 3 | 3 d6314349 | yes | none | lost: 13 lines of `confirm` after `raise Abort()` | right |
| 142 | s369 | 7 | 8 76bc91ef | yes | none | lost: same tail of `confirm` | right |
| 145 | s144 | 2 | 3 d8c31c30 | no | base | batch's own `sys.stdout.write(out + "\n")` | - |
| 145 | s145 | 12 | 13 54f1c3a1 | no | base | same | - |
| 146 | s173 | 2 | 2 29facca1 | yes | none | lost: 8 statements of `echo` | right |
| 146 | s453 | 7 | 7 dd6f422f | yes | none | lost: `echo(` in `version_option` | right |
| 146 | s461 | 12 | 13 d9fbed9c | no | base | batch's own `callback=callback` return | - |
| 146 | s463 | 17 | 18 a2364e79 | no | restore | a later write in reply 17 holds 2 of 2 | - |
| 146 | s464 | 10 | 11 eb2d4777 | no | base | batch's own `if show_python:` | - |
| 147 | s132 | 17 | 17 b3803fb9 | no | base | batch's own JSON `TypeError` | - |
| 147 | s139 | 2 | 3 4b040270 | yes | none | lost: `file.write(out)`, `file.flush()` | right |
| 147 | s146 | 2 | 6 eea404fc | yes | none | lost: same, later writes hold 0 of 2 | right |
| 147 | s158 | 5 | 6 c8399628 | yes | none | lost: `file.write`, `file.flush` of `echo` | right |
| 149 | s192 | 15 | 16 39f9365f | yes | none | meant: the write changes the line to `except (KeyboardInterrupt, EOFError, RuntimeError):` | **wrong** |
| 149 | s228 | 3 | 3 6ea9f903 | yes | none | lost: `if value in ("y", "yes"):` after the same `except` change | right |
| 151 | s132 | 14 | 15 e2dd0202 | no | base | batch's own encoded `file.write` | - |
| 151 | s138 | 19 | 21 dc0c4bc2 | yes | none | lost: `if isinstance(out, str):` | right |
| 151 | s297 | 10 | 10 3b676581 | yes | none | lost: `echo(` | right |
| 151 | s314 | 6 | 7 c5855920 | yes | none | lost: `if not value or ctx.resilient_parsing:` | right |
| 152 | s291 | 8 | 8 0f141faa | yes | none | lost: 6 `kwargs.setdefault` and the return | right |
| 152 | s292 | 2 | 20 6fbd3c48 | yes | none | lost: `echo(`, `ctx.exit()`, later writes hold at most 4 of 5 | right |
| 152 | s294 | 12 | 13 2db721b5 | no | base | batch's own `show_python` lines | - |
| 153 | s131 | 3 | 4 e510a1d8 | no | base | batch's own `print(json.dumps(...))` | - |
| 153 | s282 | 10 | 10 fff89922 | yes | none | lost: `echo(`, `ctx.exit()` (frame 140's case) | right |
| 153 | s283 | 8 | 8 f9c8211f | yes | none | lost: `if version is None:` | right |
| 154 | s340 | 7 | 14 1e9925fc | yes | none | lost: `if not param_decls:` and 6 `kwargs` lines, writes in replies 8 and 12 hold 0 of 7 | right |
| 154 | s341 | 16 | 17 b7527ee3 | yes | none | lost: `if version is None:` and the version lines | right |
| 154 | s343 | 5 | 6 b84bd0a8 | yes | none | lost: `if message is None:` and the `callback` head | right |
| 154 | s346 | 3 | 5 ea0a1e95 | yes | none | lost: 8 statements, writes hold 1 of 8 | right |
| 154 | s379 | 3 | 4 6aa3b5f2 | no | base | `if f is None:` at line 433 (reasoned: batch's own decorator form, not checked against the base) | - |
| 154 | s381 | 3 | 4 a78d06a3 | no | base | batch's own single-quoted `option('--version', ...)` | - |
| 154 | s388 | 3 | 5 a90c7495 | yes | none | lost: `echo(version_msg)` (the case that `_unread_drop_refusal` cites) | right |

Notes on the judgement:

- s192 is wrong (reasoned: the noting write's text in reply 15 holds
  `except (KeyboardInterrupt, EOFError, RuntimeError):`). The statement is
  changed, not lost. The door compares statement text, so a changed line
  reads as a removed line. The note's own words cannot tell the two apart.
- s388 is counted as refused (reasoned: `_unread_drop_refusal` names s388
  as its target case). The base-commit rule decides it. If an earlier
  session of the same batch added `echo(version_msg)`, the base does not
  hold it and the door does not refuse. This read did not open the base.
- s379 is the least sure "no" (reasoned only).
- The door's notes outlive a session within a batch. This count holds a
  note and a commit in the same session only, as the brief asks. A retry
  session that commits under an earlier session's note is not counted.

## Usage

About 60k tokens, no sub-agents.
