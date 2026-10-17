# Frame 273, review 1: the constant-assertion door and `or True`

Read-only diff review of commit 000dfa78 (frame 273, pass 1) on the worktree C:/Users/roman/rota_r273.
Reviewer: an Opus agent, 2026-10-17 01:09 (from the clock).
Verdict: accept. 0 high findings, 1 low finding.

## (a) Verdicts

1. Narrowness: CONFIRMED narrow. Every shape in the brief gives the expected result through `tests.encode`. The predicate fires on 1 of 429 distinct run-database bodies and on 0 of 798 distinct cassette bodies.
2. Wall text and door order: CONFIRMED correct. `tree` comes from `_ast.parse(body)` at api.py:7284, and `body` is not reassigned before the door. The quote is right for a leading newline, CRLF and tab indent. The new Wall raises first. The old text is unchanged byte for byte. A `pytest.raises` body with `or True` is admitted.
3. The hunk alone: CONFIRMED. The commit touches two files and removes one line, the old condition. At the parent, the red test fails with `DID NOT RAISE` and the other 22 tests pass. In the worktree, 23 tests pass.

## (b) Findings

1. LOW, CONFIRMED. rota/roles/api.py:7707 and 7709. The Wall text always says "the `or True`", whatever the truthy operand is. Probe p1 shows `assert x or 1` and `assert x or 's'` get "the `or True` makes the assertion true" and "Remove the `or True`". `assert True or x` gets the same words. The commit body says the refusal "names the operand", and it does not. The quoted line still shows the real operand, so a seat can see the operand. The risk is low because 0 of 1227 recorded bodies use a non-True operand. Fix: build the operand text from `_ast.unparse(v)` of the first truthy Constant in `or_true.test.values`, and use it in both places.

Outside the points (no finding):

- Night 106 body `tst_cr3_eof_default_false` has one `or <truthy>` assert beside real asserts. The door admits it, as the brief requires. The new predicate does not change it.
- The predicate does not catch other always-true shapes, for example `assert x or [1]` or `assert not False`. That is in line with the frame 147 rule to stay narrow. No record shows such a body.

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1cf2843b-91ea-4332-96ca-93eb8010ff0b/scratchpad/r273/.

- p1_shapes.py: runs `tests.encode` from the worktree on a fresh database per shape. Results: `or True` WALL. `and True` ADMIT. `or y` ADMIT. `(x or True) and y` ADMIT. `or 1` WALL. `or 's'` WALL. `or False` ADMIT. `or None` ADMIT. `or True` with `assert cmd1() == 1` ADMIT. `True or x` WALL. `or True, 'm'` WALL. `assert True` with `or True` WALL (new text). `or True` with `pytest.raises` ADMIT. Leading newline, CRLF and tab indent: WALL, and each quotes `assert hasattr(cmd1, '_show_python') or True` exactly.
- f273/count.py (the implementer's): re-run. Its `vacuous` and `raises_a_check` match api.py:7679 to 7698 token for token. Result: 1 new fire of 1314 rows over 31 nights, `tst_ver_opt_show_py` on night 152. 0 old fires.
- p2_sweep.py and p2b_sweep.py: every `.rota/*.db` with a `tests` table, read-only. 429 distinct bodies. 1 new fire, the same night 152 body. 1 admitted body with a partial vacuous `or`. The cassette part of p2 failed on a wrong column name, and p2b found 0 bodies because the cassettes store calls as text.
- p3_cassettes.py: parses `tests.encode(...)` calls from the `completion` text of tests/rota/cassettes.db, read-only. 3873 calls, 798 distinct bodies. 0 new fires. 0 partial vacuous `or` bodies.
- parent/: `git archive 000dfa78^` of rota, tests, pytest.ini, pyproject.toml and rota_serial_plugin.py, with the commit's test file copied in. `pytest tests/rota/test_triage_fork.py -q -n0`: 1 failed (`test_an_or_true_on_every_assert_is_refused`, `DID NOT RAISE <class 'ValueError'>`), 22 passed. `rota.__file__` pointed to the scratch tree.
- Worktree: `pytest tests/rota/test_triage_fork.py -q`: 23 passed in 4.15 s. `git diff` against the parent shows 1 removed line in api.py. The old Wall text appears once in the parent. `git status` in the worktree is clean.

## (d) Usage

Reviewer estimate, about 25k input tokens and about 9k output tokens, about 34k in all. Read the harness line for the true count.
