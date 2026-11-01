# Review p2 of frame 356: commit eeed30cc

Verdict: the claim holds for a top-level dotted ref, and the method half has two defects. The review has 2 high and 3 low findings. Points: 1 holds in part, 2 holds, 3 holds, 4 holds with a changed offer, 5 finds no hunk outside the claim, 6 holds. Tests: 14 passed in the frame 356 file, 131 passed in the ten vet and criteria files, and 1465 passed in the 40 encode-door files, 0 failed.

## (a) Verdicts on the points

1. Holds in part. `_resolve_surface` on dry1's copy gives these grains. The vet stores the same at specify and at repair, except where noted.
   - `click.pause`, `click.pause()`, `pause`, `click.termui.pause` and `src/click/termui.py::pause` give `src/click/termui.py::pause`.
   - `click.termui.getchar` gives `src/click/termui.py::getchar`.
   - `click.Context.invoke` gives `src/click/core.py::Context.invoke`.
   - `os.path.echo` gives no grain. The vet keeps it as written at specify and at repair (finding 4).
   - `click.nothing_here` gives no grain. The vet keeps it at specify, and the repair door refuses it.
   - `click.Context.nothing_here` and `click.Context.invok` give a grain for a method that does not exist (finding 1).
2. Holds. The prefix `click` admits 17 modules, every `click.*` module of the index, and nothing in `examples` or `tests`. The prefix `cli` does not admit `click.termui`. It admits one module, `examples.complex.complex.cli`, by the tail rule. The proper prefix `click.term` admits 0 modules, so `click.term.pause` gives no grain. The tail `termui` admits `click.termui` and `examples.termui.termui`, and `_program_rank` picks the program row.
3. Holds. With the stored ref `click.pause`, the door passes `import click` with `click.pause()`, `from click import pause` with `pause()`, and `from click import termui` with `termui.pause()`. The import door does not fire, because the stored ref has no `::`. A body that calls only `click.echo('x')` gets this refusal: "this test never calls 'click.pause', the surface the criterion names -- call it and assert on what it returns or does. A test that calls something else instead (a mocked builtin, a different function) cannot tell a correct click.pause from a stub that never runs".
4. Holds with a changed offer. `tests.triage(ctx, criterion_id, verdict, request_span=None, criterion_span=None)` exists at `rota/roles/api.py:8274`. The verdict `cannot` writes nothing to the criterion. It returns a `next` line that tells the Tester to send `msg.question_terminologist`, or `msg.question_vision_keeper` after two answers. Only `tests_missing.tools` holds `tests.triage`. The `answer` and `challenge` modes do not. So the commit offers `msg.question_terminologist` with the criterion in `refs` in place of `tests.triage`, and all three Tester modes hold that call. The brief's claim names `tests.triage`. The commit message and the addendum of the pass report name the question. A surface of one phrase, `press any key`, gets this refusal: "the criterion names the surface 'press any key', and the index holds no such surface. No part of it is a name, so no test can call it. Send msg.question_terminologist(refs=['c_1'], question='the surface names no callable: which callable does a test call?')".
5. Finds no hunk outside the claim. The near-match scan and the `bare` name use `_surface_text`, and that serves the `()` part of the claim. One reach is outside the claim (finding 5).
6. Holds. `tests/rota/test_frame356_dotted_surface.py`: 14 passed in 6.11s. The new file and the nine files of review 1: 131 passed in 72.90s. The 39 files that call `tests.encode`, with `test_f25_offers_in_mode.py`: 1465 passed, 2 skipped, 3 xfailed in 609.51s. All runs used `-n0`.

## (b) Findings

1. **A dotted method ref resolves for any method name after a class.** `rota/roles/api.py:5622` to `:5623`. High. CONFIRMED. `_dotted_rows` adds the last segment to the class grain and does not check that the class defines it. On dry1's copy, `click.Context.invok` stores `src/click/core.py::Context.invok`, and `click.Context.nothing_here` stores `src/click/core.py::Context.nothing_here`. Both pass at specify and at repair. So the method form skips the near-match refusal for a typo, and the repair door's rule that a surface exists (DECISIONS 1056, e417a94c). The encode door then passes a body that calls `.invok(...)`. Fix: build the method grain only when the class body defines the method, for example by an AST read of the class's file, and else fall through to the path for a ref the index does not hold.
2. **A stored method grain meets the import door with a hint that does not parse.** `rota/roles/api.py:11039`. High. CONFIRMED. The vet now stores `src/click/core.py::Context.invoke` for a fresh method criterion. A body with `from click import Context` gets the hint to import `from click.core import Context.invoke`. The door reads `import click` the same way. That import line is a syntax error, so the Tester cannot follow the hint. Only `from click.core import Context` passes. The test file stores the dotted ref `click.Context.invoke` and not the grain, so no test meets this path. Fix: build the hint from the first dotted segment of the name, `Context`, and add a test that stores the method grain.
3. **The import door refuses `import click` for a stored grain, and dry1's stored dotted ref passes it.** `rota/roles/api.py:11024` to `:11039`. Low. CONFIRMED in review 1 (finding 4), and the code is unchanged here. A fresh `click.pause` criterion stores the grain. So the Tester gets the hint `from click.termui import pause` where dry1's old criteria pass `import click`. The Tester can follow that hint. Fix: as review 1 finding 4, accept a package that re-exports the surface name.
4. **A dotted ref with a wrong module part is kept as written at repair.** `rota/roles/api.py:5776` to `:5783`. Low. CONFIRMED. `os.path.echo`, `cli.pause`, `click.term.pause` and `tests.pause` pass the repair door, because the bare name is in the tree. The encode door then accepts any call of `echo` or `pause`. The near-match scan reads the whole dotted text, so it finds no neighbour. Fix: at repair, refuse a dotted ref whose last segment has rows that no module part fits, and name those rows.
5. **Outside the points: the wider `surface_names` also feeds the misplaced-name door.** `rota/roles/api.py:5680` and `:10989`. Low. PLAUSIBLE. The set now holds the bare method name, such as `invoke`, and the last segment of a ref the index does not hold. A test that imports such a name from a module that lacks it skips the refusal that says no criterion names it, and it gets the second refusal. The pass report names the same doubt. Fix: keep a separate set of grain names for the misplaced-name door.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/393648aa-e5f9-4235-ad76-56489455e14e/scratchpad/f356r2/`. Each ran from the worktree root `C:/Users/roman/rota_f354r` with `ROTA_MODEL=qwen3:8b`. The file `dry1.db` there is a copy of `dry1w3/dry1.db`.

- `p1_resolve.py`: runs `_resolve_surface`, and `_vet_surface` with `required` False and True, on 19 refs. It also lists the modules that the prefixes `click`, `cli`, `click.term`, `termui` and `src` admit.
- `test_p3_encode.py`: a pytest file that reuses the `tester` fixture of the frame 356 test file. It runs `tests.encode` on 9 pairs of surface and body, the method grain and the phrase surface among them.
- `p4_testclass.py`: checks that a method ref on a test class is still refused as a test.
- pytest with `-n0`: the frame 356 file, the ten vet and criteria files, and the 39 encode-door files with `test_f25_offers_in_mode.py`.

## (d) Usage

- Input tokens: about 60k in context at the end. This is an estimate, because the harness shows no exact count.
- Output tokens: about 12k, also an estimate.
- Total: about 72k.
