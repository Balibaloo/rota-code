# Frame 343, review of pass 1 and pass 1b (685f44dc, ceab9a42 on f343)

Verdict: the pass fixes the red case, and it lands through the commit. Three low findings remain on paths that no recorded case renders. No finding is high.

## (a) The verdict on each point

1. Yes. The offered call lands as given, and the commit stores `t_c1` at the beside path (probe P1).
2. Yes, one kept offer can. The stored-path offer and the clash door refuse each other when a Tester row and a project row share a file (finding 3). No ninth filled offer exists. The two `then=(AGAIN,)` offers re-send the original path by design.
3. Yes for every form that `inherit` makes a row. `conftest.py` and a path with `::` never reach the helper. A second criterion gets a distinct name (probe P2).
4. No wrong offer in a live state. A Tester replace at a project file needs a shared file, and that state gives a loop (finding 3).
5. Defect unlikely in either route. The missing-import route can take two hops for a project id (finding 4, outside).
6. No contradiction. The beside name keeps the form `tests/test_<thing>.py` for a project file under `tests/`.
7. No. Every route names a path that no other row of the batch holds. The challenge exception replaces the project row and does not share its file.

## (b) Findings

1. `rota/roles/api.py` 10856. Severity low. CONFIRMED by probe P3. A challenge wake that names an unfixed project row (criterion NULL) gets the beside offer for a new id. The challenged project test stays, and a second test runs beside it. This is the left-over test of frame 123. The exception tests `clash["criterion_id"] == criterion_id`, and an unfixed project row has no criterion. Before the pass, the door gave the bare text with no offer. Frame 128 holds this question open.
   Fix: test only `_wake_challenges(ctx, clash["id"])` in the exception, and offer `id=clash["id"]` at the project file.
2. `rota/roles/api.py` 10856. Severity low. CONFIRMED by probe P4. Outside a challenge, a project row with criterion `c1` (a landed fix) and a new id for `c1` at its file get the beside offer, and the offer lands. Criterion `c1` then has two tests in the batch. The old order offered the project id, and the project-id door refused it.
   Fix: when the clash row holds the same criterion, return the one-test note in place of the beside offer.
3. `rota/roles/api.py` 10789 and 10856. Severity low. CONFIRMED by probe P5. A Tester row `t1` and a project row at one path make a loop. The clash door offers the beside path. Then the stored-path door offers the old path again. The cycle repeated over 3 calls. Only an old run database or a hand-made row holds this state, because `inherit` skips owned paths.
   Fix: in the clash door, skip the beside offer when the seat's own stored row holds `path`.
4. Outside. `rota/roles/api.py` 9479. Severity low. PLAUSIBLE. The missing-import door runs before the project-id door. For a project id outside a challenge, it offers the beside path with the project id unchanged. The project-id door then refuses that id and offers a new id. The call lands after two hops, and the follow check counts the second refusal.
   Fix: pass `INVENT` as the id of the offer when `_project_holder` returns the seat's id outside a challenge.
5. Outside. `rota/roles/api.py` 9174. Severity low. PLAUSIBLE. The criterion part of the name has no length cap. A long criterion id in a nested folder can pass the Windows path limit of 260 characters at `materialise`.
   Fix: cut the criterion part to 40 characters before the number check.

## (c) Probes

- File: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c66eae69-d69c-45cb-8d68-947dc45d2ac1/scratchpad/f343probe/test_probe343.py`.
- Run from `C:/Users/roman/rota_p343` with pytest, `-s`, `--rootdir` set to the worktree and `api.RECORD` set to True. Result: 5 passed, and the prints held the results.
- P1 `test_red_case_lands_through_commit`: the encode at `tests/test_formatting.py` got the beside offer. The re-sent offer returned `{'id': 't_c1'}`, and `_commit` stored `('t_c1', 'c1', 'tests/test_formatting_c1.py')`.
- P2 `test_names`: `tests/unit/sub/foo_test.py` gave `tests/unit/sub/test_foo_test_c1.py`. `test_x.py` gave `test_x_c1.py`. `c-1.2` and `c_1_2` both gave `tests/test_x_c_1_2.py`, and the taken set adds `_2` when one is stored. `...` gave `tests/test_x_.py`.
- P3 `test_challenge_of_unfixed_project_row_new_id`: the challenge wake named `inh_6acc723a`, and the encode of `t_fix` got the beside offer.
- P4 `test_fixed_project_row_new_id_outside_challenge`: `t_new` for `c1` landed at `tests/test_formatting_c1.py`.
- P5 `test_coexisting_rows_replace`: the replace of `t1` alternated between the clash door and the stored-path door for 3 calls.
- Reads: `inherit` globs only `test_*.py` and `*_test.py`, so `conftest.py` never becomes a project row. The not-Python door refuses a path with `::` first. `sandbox.follow` accepts a `then=(AGAIN,)` step that meets another door.

## (d) Usage

Input about 58k tokens, output about 9k tokens, total about 67k tokens. The cap was 40k.
