# Frame 267, review 3: pass 1c at 98b7b562

Read-only review of commit 98b7b562 in the worktree C:/Users/roman/rota_review_267c (observed: 2026-10-16).
Verdict: accept. Point 1 holds, point 2 holds, point 3 finds one low residue.

## (a) Verdicts

1. REFUSED_END matches both runner sites byte for byte. CONFIRMED.
2. The new test fails at the parent db.py for the reason it names. CONFIRMED.
3. No third end line ends a session and stays in the note. One warning line can stay as the note. PLAUSIBLE, low.

## (b) Findings

1. rota/core/db.py:735 and rota/core/runner.py:4553-4554, 4561-4562. Severity: none. CONFIRMED.
   - db.py: `" was refused the same way in four turns; the session ended on it"`.
   - runner.py 4553: `f"{same[0]} was refused the same way in " f"four turns; the session ended on it"`.
   - runner.py 4561: `f"{same[0]} was refused the same way in four turns; " f"the session ended on it"`.
   - The joined text after `{same[0]}` equals REFUSED_END at both sites. The line reaches `outcome.errors` once, at runner.py:3779.
   - `endswith` matches any op name, so the check needs no op list.
   - Fix: none.
2. tests/rota/test_runner.py:1841. Severity: none. CONFIRMED.
   - With db.py from 5dded316 in a temp copy, the test fails.
   - The note was "rulings.rule was refused the same way in four turns; the session ended on it".
   - The test expected "rulings.rule: " plus S336_REFUSAL. That is the reason the docstring names.
   - At 98b7b562 the test passes, with four other note tests.
   - Fix: none.
3. rota/core/runner.py:3984. Severity: low. PLAUSIBLE.
   - The grep for "; ended" finds REPEAT_END alone (runner.py:4046). The grep for "the session ended" finds the two refusal sites alone.
   - Other error lines with "ended": "ended a tick with nothing done" (3984) and the cut line "your reply was cut at the output budget before it ended" (3857, 4957).
   - The line at 3984 is a warning. The session continues, and the next prose turn stops it, by the comment at 3982.
   - When that next turn stops the session with no new error, "ended a tick with nothing done" is the newest error and becomes the note.
   - That line says how the session behaved, not what failed. It can hide an earlier refusal. No case renders this path.
   - The cut line describes a real fault of the reply. The note may keep it.
   - Fix: add "ended a tick with nothing done" to `_is_end_line`, or record it as a known residue in a later frame.

## (c) Probes

1. Grep in the worktree: `git show 98b7b562`, and a grep of runner.py and db.py for "refused the same way", "the session ended", "; ended", REPEAT_END, REFUSED_END, `errors.append(`.
2. Temp copy in the scratchpad `p2`: `git archive 98b7b562 rota tests pyproject.toml`, then db.py from `git show 5dded316:rota/core/db.py`. Ran `pytest tests/rota/test_runner.py -k "refusal_doors_end_line or newest_fault"`: 1 failed, 1 passed. The import path was the temp copy.
3. Worktree at 98b7b562: `pytest tests/rota/test_runner.py -k "refusal_doors_end_line or newest_fault or why_no or note"`: 5 passed.

## (d) Usage

About 14k input tokens and 3k output tokens, about 17k total, by estimate. Read the harness line for the exact count.
