# Frame 306, review 2: pass 1c at 3e18df00

Verdict: accept for the branch. Pass 1c closes review 1's findings 2, 3 and 4 on the shapes that the brief names. The relay carries the ruled keys in every call order. Two low findings stay open. The row filter refuses a `ledger` id that the door and `land` can carry (finding 1). A widened relay that also carries an approved criterion keys `relay`, not `criterion_repair` (finding 2).

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r306` at 3e18df00, parent 07e4d1bc. No gate and no re-record ran.

## (a) The claim, point by point

1. Findings 2 to 4 of review 1 are closed. CONFIRMED by probe `q1_findings.py`.
   - Finding 2. On a night 144 copy, `answer_about(m399)` is `[ver_opt_show_py, tst_ver_opt_show_py_01, d_984fb7181e]`. The door refuses the key `m385` with "not a row of this question". `{ver_opt_show_py: approve}` lands.
   - Finding 3. On a night 158 copy, a new report from the Critic names only cr_2. `resolve_inbound` now gives one `prior_answers` entry, m145, with `about` `[cr_2, tst_02]` and the words of m146.
   - Finding 4. On night 158's s286 shape, the relay is `[cr_2]` in every order. That shape cannot show the change, because tst_02 travels as cr_2. On a copy where m145 and m146 carry cr_1 and no test of cr_2, a revise of cr_2 adds cr_2 to the relay. An approve of cr_2 does not add it (point 3).
2. The filter admits the nine `LEDGER_HOMES` tables and `batches`. Over nights 120 to 158 it keeps 9 batch refs and 7 criterion refs. It drops 3 message ids and 1 entry, which no door carries. It also drops 7 `ledger` ids, night 135's m119. The door carries a `ledger` id as a clarify's own ref, and `land` resolves it with a decision (nights 144 m55 and 156 m133). That is the one difference (finding 1). No admitted table holds a ref that the door cannot key.
3. Yes. CONFIRMED by probe `q3_order.py`. `ctx.writes` lives for the whole session and is committed at its end. The relay carries `[cr_1, cr_2]` when the ruling and the relay are in one reply, and when they are in two replies. Relay first: the reading door refuses the relay with "read the reply before you relay it". The ruling and a second relay then carry cr_2. The approve control carries `[cr_1]` only.
4. The diff is three files. `runner.py` changes `answer_about` (the filter) and the `prior_answers` loop of `resolve_inbound` (the match and the shown `about`). `sandbox.py` adds one loop in `_bind_send.stage`, after the reply's refs. The test file adds three tests. No other hunk. `test_frame306_clarify_about.py` gives 12 passed with `-n 0`.

## (b) Findings

1. `rota/core/runner.py` 205 to 209, the filter in `answer_about`. Severity: low. CONFIRMED. The filter drops an asker ref that is a `ledger` id, because `ledger` is not in `LEDGER_HOMES`. The door keys a `ledger` id from the clarify's own refs, and `land` closes it with a decision. Night 135's m119 had 7 such asker refs. The base before frame 306 did not key them either, so nothing regresses against d2b4f79a. The code comment says "a row a ruling can carry", and the code does not match the comment. Fix: admit an open `ledger` id too, or change the comment to name the tables the filter admits.
2. `rota/core/sandbox.py` 3635 to 3651 with `rota/core/scheduler.py` 1864 to 1870. Severity: low for the night, low for the frame. CONFIRMED. The widening adds cr_2 to a relay that already carries cr_1, which the ruling approves. After `apply_rulings`, the Terminologist's wake m150 keys `relay`. The predicate wants every ref of the relay ruled, so `criterion_repair` does not fire. The words of the revise reach a mode that cannot respecify. This is the end of night 158's s287 by a third route. It needs a clarify that carries a criterion of its own beside the asker's criterion. No night of 120 to 158 shows it. Fix: let the split send the ruled criteria in their own Terminologist relay, or drop an approved criterion from a relay that a ruled one rides.

Outside the points:

- Probe `q5_vk.py` shows that a Vision Keeper relay after the revise is split by owner. The Terminologist gets `[cr_1, cr_2]` and the Vision Keeper gets the item. The widening sends no criterion to the wrong owner. No finding.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r306b/`. Each opens a night database with `?mode=ro`. A probe that writes uses a backup copy in the same folder.

- `q2_filter.py`: nights 120 to 158, read-only. It classifies each asker ref that a clarify does not carry, by table, and reports whether `answer_about` keeps it.
- `q2b_ledger.py`: nights 120 to 158, read-only. It lists the clarifies that carry or rule a `ledger` id.
- `q1_findings.py`: night 144 and night 158 copies. It runs the door on m399 with and without `m385`. It runs `resolve_inbound` on an inserted report that names only cr_2. It runs four scripted sessions on s286's shape.
- `q3_order.py`: night 158 copies, with m145 and m146 set to carry cr_1. It runs four scripted sessions: one reply, two replies, relay first, and an approve control.
- `q5_vk.py`: the q3 shape, with a Vision Keeper relay and then a Terminologist relay.
- `q6_mode.py`: the q3 and q5 copies. It runs `apply_rulings` and prints each relay wake's mode key.
- `pytest tests/rota/test_frame306_clarify_about.py -q -n 0`: 12 passed.

## (d) Usage

- Input tokens: about 75k, from the remaining-token counter.
- Output tokens: about 12k, estimated.
- Total: about 87k. The harness does not show the exact split.
