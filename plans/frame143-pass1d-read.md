# Frame 143, surface push: pass 1d read of four Tester cases red after the push

The turns of the red runs are gone. The worktree register
`C:/Users/roman/rota_gate_223/tests/rota/cassettes.db` and the checkout register
`D:/repos/rota/tests/rota/cassettes.db` hold no run of the four cases after
2026-10-17 17:10:04 (observed: `case_runs`, max `at` per case, 2026-10-17 18:45).
The worktree's `.rota-gate.log` is empty, because the 18:40 gate run started it again (observed: 0 bytes, 18:40).
The gate's own re-record output survives in the holding session's task file
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0e37e9d7-d362-4c19-b149-990e66307aba/tasks/blx6qnz4w.output`
(mtime 18:37). This read uses its failure lines, the green runs of load 248924
in the checkout register, the case file, commit 0884ddf4 and the Tester brief.
Every claim about a red run's prompt is (reasoned), because no red prompt is on disk.

## 1. Pass lines and counts

| Case | Model | Pass line | Before the push (load 248924, 17:08 to 17:10) | After the push (re-record) |
|---|---|---|---|---|
| `...no-machine-could-check-is-vision_keepers` | qwen3:8b | 4 | 5/5 | 3/5, runs 3 and 5 red |
| `...that-contradicts-the-request-goes-back` | qwen3:8b | 4 | 5/5 | 5/5, red on the follow check |
| `...an-outside-fact-is-the-researchers` | qwen3:8b | 4 | 4/5, run 2 red | 3/5, runs 1 and 4 red |
| `...pass-a-literal-value-for-a-name-looked-up-at-run-time` | qwen3.5:9b | 3 | 3/5, runs 1 and 2 red | 1/5, runs 1, 2, 3, 5 red |

(observed: checkout register `case_runs`, and `blx6qnz4w.output` lines 7 to 18 and 64 to 112.)
The re-record header says "on qwen3:8b". The literal case's YAML pins `model: qwen3.5:9b`,
and its earlier rows carry that model (observed: the case file and the register).
That the re-record honoured the pin is (reasoned), because the red rows are gone.
The loads 248916 and 248918 gave the same counts as 248924 for all four cases (observed: the register).

## 2. What each red run did, and the prompt diff

The re-record output gives only the problem lines. The calls are not on disk.

- **vision_keepers, runs 3 and 5:** "none of the permitted answers was given; wrote
  ['tests'], sent []; forbidden write to tests: ['tst_5dd311']" and "['tst_1']".
  The case expects one question to the Terminologist or the Vision Keeper about `<c1>`,
  and forbids a write to `tests`. Before the push, all five runs called `tests.triage`, then
  `tests.encode`, and the door turned each back to a question (observed: load 248924 transcripts).
  After the push, two encodes landed as test rows.
- **outside-fact, runs 1 and 4:** "none of the permitted answers was given; wrote
  ['ledger', 'tests'], sent []; forbidden write to tests: ['tst_1']". The case expects a
  question to the Terminologist or the Researcher. The pre-push red run 2 had the same shape
  (observed: the register's `problems`).
- **contradicts, follow check:** the case passed 5/5 on its expectation. The conftest follow
  check found the `tests.encode` door at `rota/roles/api.py:7272`. The door refused with
  "c_a73c75 has no triage verdict from you yet. Call tests.triage(criterion_id='c_a73c75',
  verdict='encodable')". The replayed offer was refused again: "c_a73c75 says 'returns' and
  s_a72bbf says 'prints'. Send tests.triage(... verdict='contradicts_request' ...)".
  Before the push, all five runs called only `tests.triage` three times and never `tests.encode`
  (observed: load 248924 transcripts). So at least one post-push run called `tests.encode`.
- **literal, runs 1, 3, 5:** "expected writes to tests (1..1), got 0". Run 1 also sent an
  `answer` to the Developer, which the case forbids. **Run 2:** wrote `tst_ver_opt_show_py` and
  the body has no literal `version=` or `package_name=`. The case expects one test row that passes a literal
  version or package name. Before the push, runs 1 and 2 failed with "got 0" (observed).

**Prompt diff against the last green run** (reasoned: commit 0884ddf4 changes two things only).

1. The sentence in `rota/roles/prompts/tester/base.md`: "A body asserts what the surface
   returns, read from the pushed source, and never a value the criterion does not give."
   The system prompt of every Tester wake carries the sentence, so all four cases change.
   The `system_hash` stays `f662c313...` and `b58c7919...` on the green rows,
   and the rows went stale, which fits a change in the system text (observed: the register; reasoned: the link).
2. The push `surface path::name`, from `_criterion_surface_pushes` in `rota/core/runner.py`.
   The push reads `criteria.surface_refs`. The vision_keepers, outside-fact and contradicts
   fixtures give no `surface_refs`, and the column defaults to `'[]'` (observed:
   `rota/core/schema.sql:472` and the case file). So these three cases get **no** pushed block,
   and the sentence is their only change (reasoned: the code path).
   The literal case's criterion has `surface_refs: ["src/click/decorators.py::version_option"]`.
   Its pushed block holds the `def version_option(` lines through `-> t.Callable[[FC], FC]:`,
   with `version: str | None = None`, `package_name`, `show_python: bool = False`,
   and one return line, `return option(*param_decls, **kwargs)` (reasoned: the push's AST rules run on the case's source).
   The nested `return` at line 506 is inside a nested def and is left out.
   The block does not show the run-time lookup `if version is None and package_name is None: ... f_globals`,
   which is the fact the case is about.

## 3. Placement

The brief's four candidates, in order: the push shows a wrong surface, the sentence pulls the
seat toward a test, model noise, the fixture. The wall guide's section 4, step 2 asks for the
instrument first. The instrument is not checkable, because the red turns are gone. So each placement is (reasoned) and from one gate run, and none gates.

| Case | Placement | Push right for the surface? |
|---|---|---|
| vision_keepers | The sentence pulls the seat toward a test. The case expects a question. | No push reaches the case. |
| outside-fact | The sentence pulls toward a test. Part noise: 1 of 2 red runs has the pre-push shape and rate. | No push reaches the case. |
| contradicts | The sentence pulls toward `tests.encode`. The encode call then shows a door defect that was already there: guide cause 9. The encode door's offer names `verdict='encodable'`, and the triage door refuses that verdict for this criterion. | No push reaches the case. |
| literal | The sentence's clause "never a value the criterion does not give" contradicts the case. The case expects a literal `version=` that the criterion does not give. Part noise: 2 of 4 red runs have the pre-push rate. | The block is right as far as it goes, with the signature and the defaults. It omits the lookup lines that make the literal necessary. |

Reasons:

- The three no-surface seats called `tests.encode` before the push too, and the door turned
  them back (observed: load 248924). After the push the seats wrote rows. A sentence that says "a
  body asserts what the surface returns" assumes a body exists. A model that reads "a body"
  writes one (reasoned: the sentence is the only change in their prompt).
- These seats see "read from the pushed source", and the prompt has no pushed source. The
  sentence then names an absent fact (reasoned).
- The literal case's red rate rose from 2/5 to 4/5. The new red runs either write nothing or
  write the old body. The clause forbids the exact act the case expects (reasoned: the case's
  `text_includes_any` list against the clause).
- The fixture is not the cause for any of the four. None of the four case files changed in 0884ddf4 (observed: the stat
  lists `l1_tester.yaml` +135 lines, all for the new case; reasoned: no edit to these four ids, not diffed line by line).

## 4. Fixes, one per cause

1. **The sentence, cheap (4 cases, about 7 red runs net of the pre-push base).** Take the
   sentence out of `tester/base.md`. Put it in the pushed block's own text, so it reaches only a
   wake that carries a surface. Drop the clause "and never a value the criterion does not give".
   Write it as "A test that asserts a return value asserts what this surface returns." This
   combines the brief's options "narrow the push" and "change the sentence". Narrow the push
   further to criteria whose text names a return value only if the re-record of the literal
   case stays under its pass line. Count: vision_keepers 2 runs, outside-fact 1 net, contradicts
   the encode call behind the follow-check finding, literal 2 net. The frame's own case
   `L1-TS-assert-the-value-the-surface-returns` must re-earn on the moved sentence.
2. **The encode door's offer, cheap, cause 9 (1 finding).** When the triage door would answer
   `contradicts_request`, the encode door's offer must name that verdict and not `'encodable'`.
   The defect was there before the push. Push it as its own frame with `Site: rota/roles/api.py`,
   unless frame 143's site already holds `api.py`.
3. **Noise, no fix (about 2 runs).** Outside-fact's 1/5 base and literal's 2/5 base were red
   before the push. Re-record after fix 1. The pass lines hold or the residue is read.
4. **The literal case's wall itself, not this frame.** The push omits the lookup lines the case
   needs. The case was 3/5 at its line of 3 before the push. If it stays at or under 3/5
   after fix 1, the case belongs to the frame that owns the "name looked up at run time" wall,
   and it is not a defect of the push.

Then re-record all four plus the frame's own case. Re-records are cheap.
