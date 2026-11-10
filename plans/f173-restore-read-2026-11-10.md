# Read: the restore of removed code on dry run 8, and the rows that already hold it

Frame 173, build 3 of the order. Read-only. Sources: the run's database
`dry8/copies/final.db` (read by id and by batch id), the worktree
`D:/repos/_AI/sample_repos/icalendarI/.rota/worktrees/bg_1` (`git log`,
`git show`, `git diff`), the turn logs `dry8/turns/`, and the code at 922e79e7.

## Result

1. `touch_strays` holds the removal as one free-text `note`: "removal: `assert "\n" not in line` at line 129". No column holds the statement or its base line. The exact bytes are only in git at the fork 99619246 (observed: the row, `_removal_entry` in `rota/roles/api.py`).
2. His "keep" landed as words only: `ruled_refs` rr_997d2888b831, `approve` on bg_1, `act` None. The removal line on his page is unnumbered, so no reply can name it (observed: `render_page`, principal.py:2892).
3. The Architect's judgement made the one act: a `mistake` row at a585c4ea. `touch_mistaken` then woke the Developer s198 (observed).
4. s198 made 12 commit calls, not 13. 3 landed: 8a8eb07f (the restore), 4d42947d and fddff3af (fold changes). Nothing scopes a `touch_mistaken` wake to the restore (observed: `turns`, `git log`, `code_commit`).
5. Today one path commits in a batch worktree with no model: `lifecycle.merge` commits the tests. One path writes fork bytes into the worktree: `harness.run_at_base`, with no commit. No pick and no rebase exist (observed: grep).
6. m59 joins two facts. "after 3 attempts" is the count of the key `developer|tick:tests_failing|bg_1`. The two named files were red on run 6 only, at fddff3af (observed: `tick_attempts`, `test_run_journal`).

## 1. The rows

Two tables can hold a removal (observed: `rota/core/schema.sql` 426 and 465).

- `touch_strays(batch_id, commit_sha, path, status, note)`. `code_commit` writes one row per grain at each commit (api.py 27461 to 27483). The grain is `path::owner`. The note is `removal: ` plus each statement "at line N". N is in code.source numbering of the base, which counts from 0. Git line 130 is note line 129 (observed: `git show 99619246:...string.py`, `def _foldline` at git line 119, code.source `[118, 162]`).
- `drop_notes(batch_id, path, status, note, lines, defs, whole, noted)`. A Developer's own `dropped` note from `code.write`. bg_1 has 0 rows (observed).

The statement text and its base index are computed again at every commit. `_base_removals` reads the fork bytes through `_base_texts`, and `_removal_entry` returns `[owner, line.strip(), count]` and the index. Only the note is stored (observed: api.py 27705 to 27811). The text loses its indentation (`.strip()`).

The rows of bg_1, by batch id:

| commit | time | written by | status | note |
|---|---|---|---|---|
| 67e0b2d0 | 18:42:16 | s162, `code_commit` | open | removal: `assert "\n" not in line` at line 129 |
| a585c4ea | 18:46:39 | `code_commit`, then s197 `batches.judge_touch` | mistake | the same, then "The removal ... is a mistake. The principal explicitly stated that this line should remain ..." |
| 8a8eb07f, 4d42947d, fddff3af | 19:09 to 19:11 | none | | the restore writes no row (comment at api.py 27472) |

The row at 67e0b2d0 stays `open` on an old head (observed). The brief writes `assert " " not in line`. The line is `assert "\n" not in line`. The commit message of 8a8eb07f holds a real line break where `\n` was, and `git log` shows it as a space (observed).

The restore is not equal to the base. 8a8eb07f wrote the assert over the blank line after it. `git diff 99619246 8a8eb07f` shows the blank line gone and the escape branch of a585c4ea still in place. His m46 dropped c2, the escape handling (observed).

## 2. His word

- The page: m30, a `clarify` about bg_1. Its first line "The change removes code that no answer of yours allowed: in _foldline, the line `assert "\n" not in line`." comes from `removal_line` (principal.py 3000). m31, a `present`, carries the same line (observed: `turns/t5.txt` 60 and 70).
- His answer: m45, `converse`, to m30. The entry e_m45, verbatim: "Fold only a line longer than 75 octets, as the code does today, and keep the line assert "\n" not in line in _foldline." (observed).
- The door and the rows: rulings r_m45 and r_m45_2, both `landed`, ask m30. r_m45_2 holds `per_item {"bg_1": "approve"}`. Its one ref is rr_997d2888b831: ref bg_1, `verdict approve`, `act` None, `target_kind` None, `words` his sentence, `source reading` (observed). No `keep` act exists for a removal. `render_page` puts the removal line on top unnumbered, "so `parse_reply` reads the same order" (observed: principal.py 2888 to 2893). So the reply had no line to land on (reasoned).
- The Architect: `touch_strayed` (predicates.py 2868) woke s197 with the open row at head a585c4ea. s197 called `batches.judge_touch(mistakes=['src/icalendar/parser/string.py::_foldline'], reason=...)`. The door wrote the `mistake` row with the removal note in front of the reason (observed: api.py 29331, `tool_calls` s197 seq 6).
- The wake: `touch_mistaken` (predicates.py 2888) reads `mistake` rows at the head and woke s198, the Developer, `wake_kind tick:touch_mistaken`, detail the grain (observed).
- What the wake showed: the row with its note from `_mistake_rows` (runner.py 1156 and 536), his words m24, m45 and m46, then `[code.diff]` with `[removed lines]` `-     assert "\n" not in line` before `batches.expect` (observed: s198 turn 1, runner.py 4866). The push also held `criteria.load`, `tests.load` and `batches.expect` with the red c3 test "Unicode line exceeds 75 octets" (observed).

## 3. The restore wake

s198: developer, qwen3.5:9b, `tick:touch_mistaken`, refs bg_1, 25 turns, `committed` 1. Tools pushed before turn 1: `batches.expect`, `code.diff`, `code.probe`, `criteria.load`, `tests.load`. Tools called: `code.source` 9, `code.write` 13, `code.commit` 12, `code.diff` 1, `tests.load` 3 (observed: completions and `tool_calls`).

| # | turn | commit message, cut | the door's reply |
|---|---|---|---|
| 1 | 2 | Restore removed assert ... as per principal ruling | committed, 8a8eb07f |
| 2 | 4 | Fix unicode test to use correct string literal | nothing changed (write: span crosses blocks) |
| 3 | 6 | Fix unicode test to strip trailing \r ... | nothing changed (write: a test file is the Tester's) |
| 4 | 8 | Fix _foldline to exclude \r from byte count | nothing changed (write: start inside the docstring) |
| 5 | 9 | the same | "unchanged since you asked earlier" (write: not valid Python) |
| 6 | 11 | Fix _foldline to properly count bytes ... | committed, 4d42947d |
| 7 | 13 | Fix _foldline to properly handle multi-byte ... | nothing changed (write: drops `_unescape_string`, `validate_token`) |
| 8 | 14 | Restore _foldline with assert ... and proper folding | nothing changed |
| 9 | 15 | the same | "unchanged since you asked earlier", and NOTE: code.write refused 3 turns, not accepted again |
| 10 | 20 | Fix multi-byte UTF-8 folding ... | nothing changed (write: span crosses blocks) |
| 11 | 21 | the same | committed, fddff3af |
| 12 | 22 | the same | "done at turn 21 ... It stands" |

`tool_calls` holds 11 commit rows. Call 12 has no row (observed). W10's count of 13 is not reproduced.

Why two fold changes could land (reasoned from the observed sites):

- `code_commit` takes any write of the batch in any wake. No check in `rota/roles/api.py` names `touch_mistaken` (observed: grep finds it only in runner.py and principal.py).
- The push put the red c3 test in front of the seat, so the seat worked on it after the restore.
- The restore commit's reply named no next step. The predicate drained at 8a8eb07f, and the session ran on.
- The quarantine of `developer|tick:tests_failing|bg_1` stops new wakes of that key. It does not stop writes in another key's wake.

## 4. A commit with no model

| path | function | writes the batch worktree | commits | bytes from the fork |
|---|---|---|---|---|
| fork | `worktrees.create`, worktrees.py 123 | yes, `git worktree add` | no | it makes the fork |
| merge | `lifecycle.merge`, lifecycle.py 270 | yes, `harness.materialise` | yes, `worktrees.commit(tree, "rota: tests of ...")` at 297 | no, the Tester's bodies from the database |
| merge into the root | `worktrees.integrate`, worktrees.py 457 | no, the root | yes, `merge --no-ff` | no |
| pick | none | | | |
| rebase | none | | | |
| base run | `harness.run_at_base`, harness.py 731 | yes, then writes its own bytes back | no | yes, `_base_file` (harness.py 724, `git show base:rel`) |
| base record | `harness.record_base_run`, harness.py 671 | runs the tree as it is | no | no |
| discard | `worktrees.discard`, worktrees.py 275 | yes, `checkout HEAD` | no | no, HEAD |
| removal compare | `_base_removals`, `_base_texts`, api.py 27705 | no, reads only | no | yes |

`worktrees.commit` (worktrees.py 205) has two callers: `lifecycle.merge` and `code_commit` at api.py 27357 (observed). `worktrees.base` gives the fork as the merge base with the root (worktrees.py 366).

## 5. The stopped page

m59 is a `present` to him with the clause "The team gave up: src/icalendar/tests/test_icalendar.py and src/icalendar/tests/test_issue_116.py still fail after 3 attempts: AssertionError: assert 'foo\r\n b\r\n a\r\n r' == 'foo\r\n bar'." (observed: `turns/t6_agenda.txt` 136).

- The words come from `_key_words`, principal.py 2425. "after 3 attempts" is `n` of the quarantined key. The file names and the error come from `park_reds(conn, batch)` at the head now (observed).
- `tick_attempts`: `developer|tick:tests_failing|bg_1`, attempts 3, quarantined 1, reported 1 (observed).
- `test_run_journal`, bg_1: inh_7bed8d74 (test_icalendar.py) and inh_c55c4bf6 (test_issue_116.py) pass on runs 1 to 5 at 99619246, 67e0b2d0 and a585c4ea. Both fail on run 6 only, at fddff3af, seq 899 and 945. No run exists at 8a8eb07f or 4d42947d (observed).
- So the 3 attempts counted other red tests, and s198's fddff3af made the two named files red after the quarantine (reasoned: the key carries the batch only, the files were green at those attempts).

## 6. The reach

| carrier | reader | site | what it carries |
|---|---|---|---|
| `code.commit` reply, `removals` and `removals note` | the committing Developer | api.py 27486 | statement and base line, "the Architect judges after this session" |
| `code.commit` reply, `removals judged a mistake` | the committing Developer | api.py 27484 | the mistake note, "Put the line back, then commit" |
| `touch_strayed` wake detail | Architect | predicates.py 2868 | `path (note)` of open rows at the head |
| `touch_mistaken` wake body | Developer | runner.py 1156, `_mistake_rows` 536 | `path (note)` of mistake rows at the head |
| `code.diff`, `[removed lines]` | any seat that calls it, pushed first on `touch_mistaken` | api.py 22379 and 22484, runner.py 4866 | the removed lines as diff text |
| `code.read`, `removed lines` | Critic | api.py 24716 | the same |
| `removal_line` on every page | Principal | principal.py 2892 and 3000 | one unnumbered line, at most three statements in words |
| `merged_removal_line`, end-of-run summary | Principal | principal.py 510 | the removals of merged batches |
| quarantine words of `touch_mistaken` | Principal | principal.py 2577 | no statement: "the team could not put back code it was not asked to change" |
| `code.write` `dropped` note | Developer | api.py 26903 and 26986 | the Developer's own note, `drop_notes` |
| `mergeable` | no seat, the merge gate | lifecycle.py 1197 | holds the merge on open or mistake rows |

## Frames matched

- Frame 173 (parked) is the home. Its status of 2026-11-08 10:49 names W1 and the 19 `touch_mistaken` sessions, and says "The keyed removal line is not built" (observed).
- Frame 362 holds the correction of 2026-11-08 10:23: a restore from the stray rows needs no model, and the restore act at the stray door is in its handover (observed).
- Frame 182 matches the red-after-quarantine half of m59 by symptom only. Frames 253 and 276 cover quarantine pages, and neither names a wrong count (observed: headings).
- No heading names `restore` or `keep` (observed: grep `^### `).

## Not read

The code of `parse_reply`. The session between 67e0b2d0 and a585c4ea. `batches_strays` and its callers. The removal read beyond section D. The register case `L1-DV-put-back-a-removed-block`. Whether `park_reds` reads the head only.

## Usage

About 60k tokens of context. 34 tool calls. No file edited except this page.
