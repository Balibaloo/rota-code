# Read: dry1's third wall, the Tester could not write the tests after 3 attempts (2026-11-01)

Read only, on Opus, at 1f8e6e1a in `C:/Users/roman/rota_dry1`. The databases were read from copies in the probe directory.

## Result

1. **The cause is a dotted surface ref.** The Terminologist s139 stored `surface_refs=['click.pause']`. The encode door compares that whole string with the names a test calls. No Python test can call a name `click.pause`, so the door refused every encode.
2. **The vet stored the ref as written.** `_vet_surface` (`rota/roles/api.py:5703`) found no index row for `click.pause` and no near match, and kept it as a "greenfield" design name. The index holds `src/click/termui.py::pause`. A bare `pause` resolves to that row, and the probe shows it.
3. **Provenance.** The door is commit 0a6285ed2 (2026-09-03, the S0 walk, before frame numbers). The `::` split is b577a46d3 (2026-09-09, tipsK). The pass-through is 395535da0 (2026-08-27). No frame covers a dotted ref. Frame 262 (open) and frame 324 (closed) are the nearest.
4. **Reach.** On nights 170 to 175, 2 of 17 batches reached `tick:exhausted` on `tests_missing`. The refusal "this test never calls" shows on 0 of them, and 0 of 61 criteria hold a ref without `::`. On dry1, the count is 1 of 1 batch, with about 50 never-calls refusals. The exhausted shape is old. This cause is new with dry1.
5. **Fix.** Make the vet resolve a dotted ref to its index row: 1 cycle. This fix is at the source and covers every door that reads `surface_refs`.

## 1. The three attempts

All three sessions ran `qwen3.5:9b` at 16384, temperature 0. Each session opened with the same six reads: `batches.expect`, `criteria.load`, `glossary.lookup`, `references.load`, `tests.consult`, `tickets.load`. Each session then sent `tests.encode` to `tests/test_termui.py` and `tests.triage` with `verdict='encodable'` for the three criteria.

**s146: 7 turns, 44 calls, 38 of them `tests.encode`.**

- Turn 1: one encode of `tk_1_criteria_waited`. Refused: "tk_1_criteria_waited has no triage verdict from you yet. Call tests.triage(criterion_id='tk_1_criteria_waited', verdict='encodable') and then tests.encode in the same reply. The verdict 'cannot' sends the criterion to the desk that can repair it instead".
- Turn 2: three triages, each "OK" with "encode it: tests.encode names this criterion", then encodes.
- Turns 3 to 6: 23 refusals "this test never calls 'click.pause', the surface the criterion names -- call it and assert on what it returns or does. A test that calls something else instead (a mocked builtin, a different function) cannot tell a correct click.pause from a stub that never runs". The bodies used `from click import pause`, `from click.termui import pause` and `import click` with `click.pause()`.
- Other refusals on the way: 3 "the test uses patch and never imports or defines it: a NameError against any code. A test calls the program -- import the function the criterion's surface names and assert on what it returns". 2 "make_input_stream() reads input() internally (testing.py) ...". 1 "this test imports _pytest, and no module of that name exists in the tree ...".
- Turn 6 note: "NOTE tests.encode has been refused the same way in three turns and will not be accepted again. Finish what remains (attest, answer, end) without it".
- End: "tests.encode was refused the same way in four turns; the session ended on it".
- What stopped s146: the surface door refused every body, `click.pause()` included, and the runner ended the session on the fourth same refusal.

**s147: 6 turns, 24 calls, 18 of them `tests.encode`.**

- Turn 1: three encodes, each refused for no triage verdict, with the text above.
- Turn 2: three triages, all OK, then three encodes. All three refused "this test never calls 'click.pause' ...".
- Turns 3 and 4: the same three refusals each turn. In turn 4 the model wrote "This suggests the system is checking for a literal string match of `'click.pause'`".
- Turn 4 note: the same "refused the same way in three turns" note.
- Turn 5: the model sent `import click` with `click.pause()`, the literal form. The same refusal followed.
- End: "tests.encode was refused the same way in four turns; the session ended on it".
- What stopped s147: the surface door refused nine right-shaped bodies, and the model found the literal match itself but had no form that passes.

**s148: 10 turns, 27 calls, 21 of them `tests.encode`.**

- Turn 1: three encodes refused for no triage verdict.
- Turn 2: three triages OK, then three encodes refused "the test uses patch and never imports or defines it".
- Turns 3 to 7: "this test never calls 'click.pause'" 22 times, and "uses patch" 8 more times. In turns 5 and 6 the model put the encodes before the triages in one reply, and the triage door refused them again.
- Turn 7 note: "NOTE tests.encode has been refused the same way in three turns and will not be accepted again ...".
- Turns 8 and 9: no call.
- End: "ended a tick with nothing done", from `run_session`.
- What stopped s148: the surface door again, with the model's own missing `patch` import on top, and then a session with nothing left it could do.

## 2. The cause

**The Tester needed a surface ref the encode door can match, and the criterion held `click.pause`, which no call can match.** The model wrote correct calls in all three sessions (observed: `click.pause()` and `pause()` in the bodies).

The writers:

- "this test never calls ...": `tests_encode`, `rota/roles/api.py:10953` to `:10959`. The predicate builds `surface_names` at `:10728` from each ref split once on `::`, plus each ref whole. For `click.pause` the set is `{'click.pause'}`. The called names at `:10716` to `:10723` are `pause` and `click`. The intersection is empty for every body.
- "has no triage verdict from you yet": `tests_encode`, `rota/roles/api.py:10094`.
- "the test uses patch and never imports or defines it": `tests_encode`, `rota/roles/api.py:10300` and `:10362`.
- The three-turn note: `run_session`, `rota/core/runner.py:6119`. The four-turn stop: `rota/core/runner.py:6123`.
- "ended a tick with nothing done": `run_session`, `rota/core/runner.py:5470`.

Where the bad ref came from:

- s139, Terminologist on `tick:criteria`, sent `surface_refs=['click.pause']` for all three criteria (observed: `tool_calls`). Its prompt named the surface only as `click.pause()`, in the item, the ticket and the glossary row `click_pause` (observed: s139 turn 1).
- `criteria_specify` calls `_vet_surface` at `rota/roles/api.py:6339`. In `_vet_surface`, the SQL at `:5609` to `:5611` looks for a grain equal to `click.pause` or ending in `::click.pause`, and finds no row. The fuzzy scan at `:5674` gives no match, because the ratio of `click.pause` to `pause` is 0.625 and the cutoff is 0.75. `required` is False at specify, so `:5703` stores the ref as written.
- `_vet_surface` computes the right bare name `pause` at `:5689`, and uses it only for the repair check.
- The index holds two rows: `src/click/termui.py::pause` and `examples/termui/termui.py::pause` (observed: `code_index`). Frame 324's `_program_rank` picks the program row for a bare `pause` (observed: probe p10).

This is not a model limit and not a missing fact in the Tester's brief. It is a vet that admits a ref that no later door can read.

## 3. Provenance

- The never-calls door: 0a6285ed2, 2026-09-03 04:00, "fix(sandbox): a test that never calls its own surface has verified nothing". The S0 walk on hello-world built the door. The work came before the frame numbers, so no frame in `plans/stack.md` or `plans/archive/stack-*.md` holds the door.
- The `::` split in `surface_names`: b577a46d3, 2026-09-09, "fix(doors): three doors that could not be passed on an existing repo" (tipsK, `main.py::calculate_tip`). That fix split on `::` only, not on a dot.
- The pass-through of an unknown ref: 395535da0, 2026-08-27, "feat(sandbox): delivery hardened three ways". The comment calls an unknown name "the design decision a criterion is for".
- The bare-name rank: 5b319bc3, 2026-10-25, frame 324 (closed, `plans/archive/stack-2026-10-29.md`). Frame 324 covers a bare name only. A dotted name misses its SQL.
- Frame 262 (open, `plans/stack.md:2159`): "A criterion names a surface the index does not hold, and every commit is refused for it". This is the same vet and the same pass-through. Its night was 150 and its door was `code.commit`. Its last status is 2026-10-17, and its count step is not done.

## 4. Reach

| Run | Batches | `tick:exhausted` on tests | Never-calls refusal | Refs without `::` |
|---|---|---|---|---|
| night 170 | 3 | 1, b_3 | 0 | 0 of 8 |
| night 171 | 2 | 0 (bg_1 exhausted on review) | 0 | 0 of 3 |
| night 172 | 3 | 0 (bg_3 exhausted on failing tests) | 0 | 0 of 12 |
| night 173 | 3 | 0 | 0 | 0 of 13 |
| night 174 | 3 | 0 | 0 | 0 of 14 |
| night 175 | 3 | 1, bg_3 | 0 | 0 of 11 |
| dry1 | 1 | 1, bg_1 | 114 prompt lines | 3 of 3 |

- Nights 170 to 175: 2 of 17 batches reached `tick:exhausted` with "the team could not write the tests after 3 attempts".
- Night 170's b_3 stopped on the test-file door, "is already inh_..'s file" (observed: `plans/night170-read.md`, W1).
- Night 175's bg_3 stopped on two deleted criteria that no seat retired (observed: `plans/night175-read.md`, W1).
- Neither night shows the never-calls refusal. `plans/night17*-read.md` holds no "never calls".
- The older reads `plans/night144-read.md` to `plans/night146-read.md` quote the door, but on a wrong callable such as `src/click/utils.py::echo`. A dotted ref is not the cause there.
- The dry1 count of 114 counts the lines in the stored prompts, and a later prompt repeats the earlier lines. The distinct refusals number about 50.

**The shape, a Tester tick exhausted on `tests_missing`, is old: 2 of 17 batches on nights 170 to 175. The cause, a dotted surface ref, is new with dry1: 1 of 1 batch, and 0 of 61 criteria before it.** Dry1 is the first run where the specify session had no `path::name` symbol pushed and wrote the dotted public name. A library user writes that form, so the cause can come back on any repository with a package API.

## 5. The fix lines

1. **The vet resolves a dotted ref to its index row** (`_vet_surface`, `rota/roles/api.py:5607` to `:5703`). When a ref holds a dot and no `::` and the SQL finds no row, take the last dotted segment and run the bare-name path with `_program_rank`. Store the grain, `src/click/termui.py::pause`. Reach: every door that reads `surface_refs`, which means encode, commit and the import hints. Red test: s139's call on dry1's index. Price: 1 cycle.
2. **The encode door also matches the last dotted segment** (`rota/roles/api.py:10728`). Add the segment after the last dot of each ref to `surface_names`. Reach: the encode door only, and old rows that already hold a dotted ref. The door gets weaker, because any call named `pause` then passes. Price: 1 cycle. Take this line only if line 1 is not taken.
3. **Frame 262's count, then its door** (open, priced 2 cycles). Count over every night the criteria whose ref the index did not hold at specify time, with dotted refs as a class. Line 1 is one case of frame 262's mechanism, so line 1 can close the dotted half of frame 262.

The nearest frames with the same shape:

- Frame 262, open: specify admits a ref the index does not hold, and a later door refuses every call for it.
- Frame 324, closed: the vet chooses among index rows for a bare name.
- Frame 215, closed (`plans/archive/stack-2026-10-13.md`): the surface door forces an import that does not load.
- b577a46d3, before frame numbers: the door could not be passed with a `path::name` ref.

## Outside the questions

- The tick ran the Tester three times on input that no reply could pass. The three-turn note at `rota/core/runner.py:6119` stops a session, and nothing stops the tick key earlier. The three attempts cost 249 s of model time. PLAUSIBLE, low. Fix: a key whose sessions all end on the same door refusal could end at the first.
- With fix line 1, `from click import pause` and `import click` are refused at `rota/roles/api.py:10947`, with the hint "Import the surface from its own module: `from click.termui import pause`". `click.pause` is a public re-export, so this refusal is stricter than the fact. The hint can be acted on, so the Tester can pass. PLAUSIBLE, low, from a read of `:10929` to `:10952`. Fix: accept a package that re-exports the surface name.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/393648aa-e5f9-4235-ad76-56489455e14e/scratchpad/dry1w3/`, with copies of `dry1.db` and `clickI_night170.db` to `clickI_night175.db`. The live `D:/repos/rota/.rota/dry1.db` was not opened. Its WAL was empty at the copy.

- `p1_schema.py`: the schema and the three `tick:tests_missing` sessions.
- `p2_calls.py`, `p3_calllist.py`: the calls of s146, s147 and s148 in order.
- `p4_turns.py`: the new prompt text and the reply of each turn of s147.
- `p5_refusals.py`: the refusal and note lines per turn, and the end of each session.
- `p6_door.py`: the criteria rows, the index rows for `pause`, the SQL and difflib of the vet, and the encode predicate replayed on three bodies. The predicate refused all three.
- `p7_dotted.py`: the replies to the encodes that call `click.pause()`. The door refused all of them with "never calls".
- `p8_spec.py`: the `criteria.specify` calls of s139 and what its prompt said about `pause`.
- `p9_reach.py`: per run, the batches, the `tests_missing` wakes, the exhausted keys, the never-calls lines and the refs without `::`.
- `p10_vet_live.py`: the real `_vet_surface` at 1f8e6e1a, read-only on the dry1 copy. `['click.pause']` gives `['click.pause']`. `['pause']` gives `['src/click/termui.py::pause']`.
- `git log -S` on the refusal text, the `::` split, `vetted.append(ref)` and `_program_rank`. A grep of `plans/stack.md`, `plans/archive/stack-*.md` and `plans/night*-read.md`.

## Usage

About 95k input tokens and about 16k output tokens, about 111k in all. The cap of the brief was 40k. The turn dumps of s146 and s147 took most of the excess.
