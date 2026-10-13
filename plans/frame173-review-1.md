# Frame 173, passes 1 and 1b: the review of 80440c1e and 319c7f19

Reviewer: Opus, read-only, on worktree `C:/Users/roman/rota_rv173` at 319c7f19, removed at the end. Meta workflow for the review. Rota workflow for the door it reviews. Date: 2026-10-13.

Verdict: the passes stand, 0 high, 4 low. The mechanism meets the frame's ends-when on the three night fixtures. One register case goes stale, and the note has no length bound.

Note on the parent: the direct parent of 80440c1e is 0ac6ad69, not c0954f92. The commit between them, f252df24, is frame 213's relay fix. The red-at-parent check ran on 0ac6ad69 (observed: `git log`).

## (a) Verdicts on the seven points

1. CONFIRMED. All four night writes name the statements the status lines list. Finding 0 quotes the notes.
2. CONFIRMED with a cost. A true rewrite lands with no note. `rv = default` to `rv = None` lands with no note, the admitted cost of the same-target rule. A binding in a nested scope also hides a removed assignment (finding 1).
3. CONFIRMED. A removed `if` names its header line only, never its body. The note has no bound: 150 removed statements give a 4085-character note (finding 2).
4. CONFIRMED. `test_offers_followed.py` passes, 39 passed and 4 xfailed. The s214 refusal records the offer `To stop where while ends send end=352.` at `_end_offer`, and the lost sentence follows the offer.
5. CONFIRMED. The `a = 1` to `a = 2` refusals were unit tests in the touched files, not register cases. One register case goes stale from this frame: `L1-DV-read-the-map-not-the-whole-file` (finding 3).
6. CONFIRMED. On 0ac6ad69 the three night tests are red and the rewrite test is green, 3 failed and 1 passed. On 80440c1e only the s214 test is red, on the `break`. At 319c7f19 `test_desk_guards.py` gives 333 passed.
7. CONFIRMED. The gate shows 8 new reds, all in the known set, 1 flaky. The stale line holds 2 cases, and one of them is new (finding 3).

## (b) Findings

0. Point 1 evidence, not a defect (observed: probe 1, 2026-10-13).
   - s214, `end=-1` refusal: "To stop where while ends send end=352. A write to start=342, end=352 removes `if value in ("y", "yes"):` at line 342, `break` at line 351, and your text does not hold them. To start after confirm send start=355. To replace the whole top-level statements send start=288, end=1024."
   - s214, `end=352` write, `dropped`: "This write removes 2 statements that your text does not hold: `if value in ("y", "yes"):` at line 342, `break` at line 351."
   - s552, `dropped`: "This write removes 6 statements that your text does not hold: `kwargs.setdefault("is_flag", True)` at line 558, `kwargs.setdefault("expose_value", False)` at line 559, `kwargs.setdefault("is_eager", True)` at line 560, `kwargs.setdefault("help", _("Show the version and exit."))` at line 561, `kwargs["callback"] = callback` at line 562, `return option(*param_decls, **kwargs)` at line 563." The status line names these six.
   - s386, `dropped`, 597 characters: "This write removes 10 statements that your text does not hold: `if message is None:` at line 487, `if version is None and package_name is None:` at line 490, `def callback(ctx: Context, param: Parameter, value: bool) ->` at line 507, `if not param_decls:` at line 559, `kwargs.setdefault("is_flag", True)` at line 562, `kwargs.setdefault("expose_value", False)` at line 563, `kwargs.setdefault("is_eager", True)` at line 564, `kwargs.setdefault("help", _("Show the version and exit."))` at line 565, `kwargs["callback"] = callback` at line 566, `return option(*param_decls, **kwargs)` at line 567."

1. `rota/roles/api.py`, `_lost_statements`, the `bound` set. Low. CONFIRMED (observed: probe P2FAR). The same-target rule collects targets from every node of the text, nested scopes included. A span of `rv = load()` and `check(rv)`, replaced by a text with `def inner(): rv = 0` and `check(rv)`, drops `rv = load()` with no note. Probe P2VALUE: `rv = default` to `rv = None` also lands with no note. The second case is the admitted cost, because the frame asks for a removed statement, not a changed one.
   Fix: collect `bound` from the text's statements at the span's own level, not from `ast.walk` into nested defs.

2. `rota/roles/api.py`, `_lost_sentence`, `_drop_note` and `_end_lost`. Low. CONFIRMED (observed: probes P3LONG and P4LONG). A 150-statement span replaced by `pass` gives a 4085-character note. The refusal with the same list is 4476 characters and writes 151 `line_text` facts. A removed compound statement names its header line alone, so a body never adds to the list (probe P3COMPOUND gave "`if x:` at line 1"). The night cases stay short: s386 is 597 characters.
   Fix: cap the list at about eight statements, close with "and K more", and cap the facts the same way.

3. Register case `L1-DV-read-the-map-not-the-whole-file`. Low. CONFIRMED (observed: the case passes on 0ac6ad69 with the same register, and is STALE at 319c7f19 with "no recording for the current prompt"). The case writes to `src/pkg/termui.py`, so a new sentence in a span result changes a later prompt. The pass report predicted this class at its line 41.
   Fix: re-record the case by its id when the main card is free.

4. `rota/roles/api.py`, `_lost_statements`, `held` is a set of line keys. Low. PLAUSIBLE (reasoned: a set ignores how often a line occurs). A span with two `break` lines or two `return None` lines, rewritten with one, names neither. The same holds for any repeated call line.
   Fix: count the keys with a `Counter` and name the surplus occurrences.

Outside the points: the frame's status lines also name s209 (night 145) and s246 (night 128). No fixture replays them, so the replay covers three of the five named writes (reasoned: the test diff holds three night tests).

## The gate (point 7)

The gate ran from the worktree with the checkout's `.rota-gate.json` and `tests/rota/cassettes.db` copied in, `pragma quick_check` ok, unpiped to a scratch file. The five lines:

- `suite: 31 failed, 3851 passed, 35 skipped, 17 xfailed, 30 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)`
- `new reds (8)`: `test_invoke_door::test_a_session_with_no_batch_reads_the_root` and `test_scene_two_batches::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`, the 2 HEAD reds. `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row` and `L1-AR-route-an-escalation`, the 2 Architect cases. `L1-DV-apply-the-answer-and-carry-on`, frame 224. `L2-DV-name-the-block-rather-than-retry` and `L2-DV-name-the-deferred-batch-not-the-running-one`, frame 204. `test_scene_challenged_again::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op`, flaky by the gate's own line. No red falls outside the known set. `test_map::test_every_op_joins_a_definition` stayed green.
- `reds gone (2)`: `L1-VK-a-statement-on-an-existing-account-is-a-behaviour`, `L3-a-failed-verdict-turns-into-a-fix`.
- `stale (2)`: `L1-DV-read-the-map-not-the-whole-file (stale by its failure)`, `L3-a-failed-verdict-turns-into-a-fix (stale by its failure) (+2 -0 against baseline)`.
- `time: 683.2s, model qwen3:8b, temp root C:/Users/roman/rota_gate/tmp, baseline 5d68808 2026-10-11 02:11`

Caution for the reader: the probe file `tests/rota/test_zz_rv173_probe.py` sat in the worktree during the gate. The passed count holds its 8 tests. No red comes from the probe file.

## (c) Probes

- Probe file `C:/Users/roman/rota_rv173/tests/rota/test_zz_rv173_probe.py`, untracked, removed. It ran the s214, s386 and s552 writes on the pass's fixtures through `sb.call("code.write")`. It also ran P2VALUE, P2FAR, P3COMPOUND, P3LONG, P4LONG and P4OFFERS on small `m.py` files.
- `pytest tests/rota/test_offers_followed.py` at 319c7f19: 39 passed, 4 xfailed.
- Worktree `C:/Users/roman/rota_rv173p` at 0ac6ad69, with the three fixtures and the 319c7f19 test file copied in untracked: 3 failed, 1 passed. The same worktree ran `L1-DV-read-the-map-not-the-whole-file` with the register: 1 passed.
- Worktree `C:/Users/roman/rota_rv173q` at 80440c1e, with the 319c7f19 test file: the s214 test failed on the `break`, 3 passed.
- `pytest tests/rota/test_desk_guards.py` at 319c7f19: 333 passed.
- The gate: `python -m rota.tools.gate` in `C:/Users/roman/rota_rv173`. Its output is `rv173_gate.txt` in the session scratchpad.
- All three worktrees are removed.

## (d) Usage

About 57k input tokens, about 10k output tokens, about 67k total, against a cap of 70k (reasoned: the session's token counter, not the harness line).
